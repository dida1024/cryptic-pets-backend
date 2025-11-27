"""Unit tests for User command handlers."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from application.users.command_handlers import (
    CreateUserHandler,
    DeleteUserHandler,
    UpdatePasswordHandler,
    UpdateUserHandler,
)
from application.users.commands import (
    CreateUserCommand,
    DeleteUserCommand,
    UpdatePasswordCommand,
    UpdateUserCommand,
)
from domain.users.entities import User
from domain.users.exceptions import (
    DuplicateEmailError,
    DuplicateUsernameError,
    InvalidCredentialsError,
    UserNotFoundError,
    WeakPasswordError,
)
from domain.users.services import PasswordPolicy
from domain.users.value_objects import UserTypeEnum


class MockPasswordHasher:
    """Mock password hasher for testing."""

    def hash(self, password: str) -> str:
        """Return a predictable hash for testing."""
        return f"hashed_{password}"

    def verify(self, password: str, hashed: str) -> bool:
        """Verify by checking if the hash matches our mock format."""
        return hashed == f"hashed_{password}"


class TestCreateUserHandler:
    """Test cases for CreateUserHandler."""

    @pytest.fixture
    def mock_repository(self):
        """Create a mock user repository."""
        repo = MagicMock()
        repo.exists_by_username = AsyncMock(return_value=False)
        repo.exists_by_email = AsyncMock(return_value=False)
        repo.create = AsyncMock()
        return repo

    @pytest.fixture
    def mock_password_hasher(self):
        """Create a mock password hasher."""
        return MockPasswordHasher()

    @pytest.fixture
    def password_policy(self):
        """Create a lenient password policy for testing."""
        return PasswordPolicy(
            min_length=1,
            require_uppercase=False,
            require_lowercase=False,
            require_digit=False,
            require_special=False,
        )

    @pytest.fixture
    def handler(self, mock_repository, mock_password_hasher, password_policy):
        """Create a CreateUserHandler instance."""
        return CreateUserHandler(mock_repository, mock_password_hasher, password_policy)

    @pytest.mark.anyio
    async def test_create_user_success(self, handler, mock_repository):
        """Test successful user creation."""
        command = CreateUserCommand(
            username="newuser",
            email="new@example.com",
            password="securepassword123",
            full_name="New User",
        )

        # Setup mock to return the created user
        def capture_user(user):
            return user

        mock_repository.create.side_effect = capture_user

        result = await handler.handle(command)

        assert result.username == "newuser"
        assert result.email == "new@example.com"
        assert result.full_name == "New User"
        assert result.user_type == UserTypeEnum.USER
        assert result.is_active is True
        assert result.id is not None
        # Password should be hashed using mock hasher
        assert result.hashed_password == "hashed_securepassword123"

        mock_repository.create.assert_called_once()

    @pytest.mark.anyio
    async def test_create_user_with_admin_type(self, handler, mock_repository):
        """Test creating admin user."""
        command = CreateUserCommand(
            username="adminuser",
            email="admin@example.com",
            password="adminpass123",
            user_type=UserTypeEnum.ADMIN,
        )

        def capture_user(user):
            return user

        mock_repository.create.side_effect = capture_user

        result = await handler.handle(command)

        assert result.user_type == UserTypeEnum.ADMIN

    @pytest.mark.anyio
    async def test_create_user_duplicate_username(self, handler, mock_repository):
        """Test user creation fails with duplicate username."""
        mock_repository.exists_by_username.return_value = True

        command = CreateUserCommand(
            username="existinguser",
            email="new@example.com",
            password="password123",
        )

        with pytest.raises(DuplicateUsernameError):
            await handler.handle(command)

        mock_repository.create.assert_not_called()

    @pytest.mark.anyio
    async def test_create_user_duplicate_email(self, handler, mock_repository):
        """Test user creation fails with duplicate email."""
        mock_repository.exists_by_email.return_value = True

        command = CreateUserCommand(
            username="newuser",
            email="existing@example.com",
            password="password123",
        )

        with pytest.raises(DuplicateEmailError):
            await handler.handle(command)

        mock_repository.create.assert_not_called()

    @pytest.mark.anyio
    async def test_create_user_adds_domain_event(self, handler, mock_repository):
        """Test that user creation adds domain event."""

        def capture_user(user):
            # Check that domain event was added before save
            events = user.get_domain_events()
            assert len(events) == 1
            assert events[0].user_id == user.id
            assert events[0].username == user.username
            return user

        mock_repository.create.side_effect = capture_user

        command = CreateUserCommand(
            username="newuser",
            email="new@example.com",
            password="password123",
        )

        await handler.handle(command)

    @pytest.mark.anyio
    async def test_create_user_weak_password(self, mock_repository, mock_password_hasher):
        """Test user creation fails with weak password."""
        # Use strict password policy
        strict_policy = PasswordPolicy(
            min_length=8,
            require_uppercase=True,
            require_lowercase=True,
            require_digit=True,
        )
        handler = CreateUserHandler(mock_repository, mock_password_hasher, strict_policy)

        command = CreateUserCommand(
            username="newuser",
            email="new@example.com",
            password="weak",  # Too short, no uppercase, no digit
        )

        with pytest.raises(WeakPasswordError):
            await handler.handle(command)

        mock_repository.create.assert_not_called()


class TestUpdateUserHandler:
    """Test cases for UpdateUserHandler."""

    @pytest.fixture
    def existing_user(self):
        """Create an existing user for testing."""
        return User(
            id="user-123",
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashed_password",
            user_type=UserTypeEnum.USER,
            is_active=True,
        )

    @pytest.fixture
    def mock_repository(self, existing_user):
        """Create a mock user repository."""
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=existing_user)
        repo.exists_by_username = AsyncMock(return_value=False)
        repo.exists_by_email = AsyncMock(return_value=False)
        repo.update = AsyncMock(side_effect=lambda user: user)
        return repo

    @pytest.fixture
    def handler(self, mock_repository):
        """Create an UpdateUserHandler instance."""
        return UpdateUserHandler(mock_repository)

    @pytest.mark.anyio
    async def test_update_user_full_name(self, handler, mock_repository):
        """Test updating user's full name."""
        command = UpdateUserCommand(
            user_id="user-123",
            full_name="Updated Name",
        )

        result = await handler.handle(command)

        assert result.full_name == "Updated Name"
        mock_repository.update.assert_called_once()

    @pytest.mark.anyio
    async def test_update_user_username(self, handler, mock_repository):
        """Test updating user's username."""
        command = UpdateUserCommand(
            user_id="user-123",
            username="newusername",
        )

        result = await handler.handle(command)

        assert result.username == "newusername"

    @pytest.mark.anyio
    async def test_update_user_email(self, handler, mock_repository):
        """Test updating user's email."""
        command = UpdateUserCommand(
            user_id="user-123",
            email="newemail@example.com",
        )

        result = await handler.handle(command)

        assert result.email == "newemail@example.com"

    @pytest.mark.anyio
    async def test_update_user_not_found(self, handler, mock_repository):
        """Test update fails when user not found."""
        mock_repository.get_by_id.return_value = None

        command = UpdateUserCommand(
            user_id="nonexistent",
            full_name="Name",
        )

        with pytest.raises(UserNotFoundError):
            await handler.handle(command)

    @pytest.mark.anyio
    async def test_update_user_duplicate_username(self, handler, mock_repository):
        """Test update fails with duplicate username."""
        mock_repository.exists_by_username.return_value = True

        command = UpdateUserCommand(
            user_id="user-123",
            username="existinguser",
        )

        with pytest.raises(DuplicateUsernameError):
            await handler.handle(command)

    @pytest.mark.anyio
    async def test_update_user_duplicate_email(self, handler, mock_repository):
        """Test update fails with duplicate email."""
        mock_repository.exists_by_email.return_value = True

        command = UpdateUserCommand(
            user_id="user-123",
            email="existing@example.com",
        )

        with pytest.raises(DuplicateEmailError):
            await handler.handle(command)

    @pytest.mark.anyio
    async def test_update_user_same_username_allowed(
        self, handler, mock_repository, existing_user
    ):
        """Test that keeping same username doesn't trigger duplicate check."""
        command = UpdateUserCommand(
            user_id="user-123",
            username="testuser",  # Same as existing
        )

        # Should not check for duplicates when username unchanged
        result = await handler.handle(command)

        assert result.username == "testuser"
        mock_repository.exists_by_username.assert_not_called()

    @pytest.mark.anyio
    async def test_update_user_activate(self, handler, mock_repository, existing_user):
        """Test activating a deactivated user."""
        existing_user.is_active = False

        command = UpdateUserCommand(
            user_id="user-123",
            is_active=True,
        )

        result = await handler.handle(command)

        assert result.is_active is True

    @pytest.mark.anyio
    async def test_update_user_deactivate(self, handler, mock_repository):
        """Test deactivating an active user."""
        command = UpdateUserCommand(
            user_id="user-123",
            is_active=False,
        )

        result = await handler.handle(command)

        assert result.is_active is False


class TestUpdatePasswordHandler:
    """Test cases for UpdatePasswordHandler."""

    @pytest.fixture
    def mock_password_hasher(self):
        """Create a mock password hasher."""
        return MockPasswordHasher()

    @pytest.fixture
    def password_policy(self):
        """Create a lenient password policy for testing."""
        return PasswordPolicy(
            min_length=1,
            require_uppercase=False,
            require_lowercase=False,
            require_digit=False,
            require_special=False,
        )

    @pytest.fixture
    def existing_user(self, mock_password_hasher):
        """Create an existing user for testing."""
        return User(
            id="user-123",
            username="testuser",
            email="test@example.com",
            hashed_password=mock_password_hasher.hash("currentpassword"),
        )

    @pytest.fixture
    def mock_repository(self, existing_user):
        """Create a mock user repository."""
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=existing_user)
        repo.update = AsyncMock(side_effect=lambda user: user)
        return repo

    @pytest.fixture
    def handler(self, mock_repository, mock_password_hasher, password_policy):
        """Create an UpdatePasswordHandler instance."""
        return UpdatePasswordHandler(mock_repository, mock_password_hasher, password_policy)

    @pytest.mark.anyio
    async def test_update_password_success(self, handler, mock_repository):
        """Test successful password update."""
        command = UpdatePasswordCommand(
            user_id="user-123",
            current_password="currentpassword",
            new_password="newpassword123",
        )

        result = await handler.handle(command)

        # Password should be changed to new hashed value
        assert result.hashed_password == "hashed_newpassword123"
        mock_repository.update.assert_called_once()

    @pytest.mark.anyio
    async def test_update_password_user_not_found(self, handler, mock_repository):
        """Test password update fails when user not found."""
        mock_repository.get_by_id.return_value = None

        command = UpdatePasswordCommand(
            user_id="nonexistent",
            current_password="current",
            new_password="newpassword",
        )

        with pytest.raises(UserNotFoundError):
            await handler.handle(command)

    @pytest.mark.anyio
    async def test_update_password_wrong_current(self, handler):
        """Test password update fails with wrong current password."""
        command = UpdatePasswordCommand(
            user_id="user-123",
            current_password="wrongpassword",
            new_password="newpassword",
        )

        with pytest.raises(InvalidCredentialsError):
            await handler.handle(command)

    @pytest.mark.anyio
    async def test_update_password_weak_new_password(
        self, mock_repository, mock_password_hasher, existing_user
    ):
        """Test password update fails with weak new password."""
        # Use strict password policy
        strict_policy = PasswordPolicy(
            min_length=8,
            require_uppercase=True,
            require_lowercase=True,
            require_digit=True,
        )
        mock_repository.get_by_id = AsyncMock(return_value=existing_user)
        handler = UpdatePasswordHandler(mock_repository, mock_password_hasher, strict_policy)

        command = UpdatePasswordCommand(
            user_id="user-123",
            current_password="currentpassword",
            new_password="weak",  # Too short
        )

        with pytest.raises(WeakPasswordError):
            await handler.handle(command)

    @pytest.mark.anyio
    async def test_update_password_adds_domain_event(self, handler, mock_repository):
        """Test that password update adds domain event."""

        def capture_user(user):
            events = user.get_domain_events()
            assert len(events) == 1
            assert events[0].user_id == user.id
            return user

        mock_repository.update.side_effect = capture_user

        command = UpdatePasswordCommand(
            user_id="user-123",
            current_password="currentpassword",
            new_password="newpassword123",
        )

        await handler.handle(command)


class TestDeleteUserHandler:
    """Test cases for DeleteUserHandler."""

    @pytest.fixture
    def existing_user(self):
        """Create an existing user for testing."""
        return User(
            id="user-123",
            username="testuser",
            email="test@example.com",
            hashed_password="hashed",
        )

    @pytest.fixture
    def mock_repository(self, existing_user):
        """Create a mock user repository."""
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=existing_user)
        repo.delete = AsyncMock(return_value=True)
        return repo

    @pytest.fixture
    def handler(self, mock_repository):
        """Create a DeleteUserHandler instance."""
        return DeleteUserHandler(mock_repository)

    @pytest.mark.anyio
    async def test_delete_user_success(self, handler, mock_repository):
        """Test successful user deletion."""
        command = DeleteUserCommand(user_id="user-123")

        result = await handler.handle(command)

        assert result is True
        mock_repository.delete.assert_called_once()

    @pytest.mark.anyio
    async def test_delete_user_not_found(self, handler, mock_repository):
        """Test deletion fails when user not found."""
        mock_repository.get_by_id.return_value = None

        command = DeleteUserCommand(user_id="nonexistent")

        with pytest.raises(UserNotFoundError):
            await handler.handle(command)

    @pytest.mark.anyio
    async def test_delete_user_adds_domain_event(self, handler, mock_repository):
        """Test that deletion adds domain event."""

        def capture_user(user):
            events = user.get_domain_events()
            assert len(events) == 1
            assert events[0].user_id == user.id
            return True

        mock_repository.delete.side_effect = capture_user

        command = DeleteUserCommand(user_id="user-123")

        await handler.handle(command)
