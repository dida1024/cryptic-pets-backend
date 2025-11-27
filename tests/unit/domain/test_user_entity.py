"""Unit tests for User entity."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from domain.users.entities import User
from domain.users.value_objects import UserTypeEnum


class TestUserEntity:
    """Test cases for User entity."""

    def test_create_user_with_required_fields(self):
        """Test creating a user with only required fields."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_123",
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_password_123"
        assert user.user_type == UserTypeEnum.USER  # default
        assert user.is_active is True  # default
        assert user.full_name is None  # optional

    def test_create_user_with_all_fields(self):
        """Test creating a user with all fields."""
        user = User(
            id="user-123",
            username="adminuser",
            email="admin@example.com",
            full_name="Admin User",
            hashed_password="hashed_password_456",
            user_type=UserTypeEnum.ADMIN,
            is_active=False,
        )

        assert user.id == "user-123"
        assert user.username == "adminuser"
        assert user.email == "admin@example.com"
        assert user.full_name == "Admin User"
        assert user.user_type == UserTypeEnum.ADMIN
        assert user.is_active is False

    def test_user_inherits_base_entity_fields(self):
        """Test that user has BaseEntity fields."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
        )

        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.is_deleted is False
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_user_mark_as_deleted(self):
        """Test soft delete functionality."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
        )
        original_updated_at = user.updated_at

        user.mark_as_deleted()

        assert user.is_deleted is True
        assert user.updated_at >= original_updated_at

    def test_user_equality_by_id(self):
        """Test that users are equal if their IDs are equal."""
        user1 = User(
            id="user-123",
            username="user1",
            email="user1@example.com",
            hashed_password="hash1",
        )
        user2 = User(
            id="user-123",
            username="user2",  # different username
            email="user2@example.com",  # different email
            hashed_password="hash2",  # different password
        )

        assert user1 == user2

    def test_user_inequality_by_id(self):
        """Test that users are not equal if their IDs differ."""
        user1 = User(
            id="user-123",
            username="testuser",
            email="test@example.com",
            hashed_password="hash",
        )
        user2 = User(
            id="user-456",
            username="testuser",  # same username
            email="test@example.com",  # same email
            hashed_password="hash",  # same password
        )

        assert user1 != user2

    def test_user_hash_by_id(self):
        """Test that user hash is based on ID."""
        user1 = User(
            id="user-123",
            username="user1",
            email="user1@example.com",
            hashed_password="hash1",
        )
        user2 = User(
            id="user-123",
            username="user2",
            email="user2@example.com",
            hashed_password="hash2",
        )

        # Same ID should have same hash
        assert hash(user1) == hash(user2)

        # Can be used in sets
        user_set = {user1, user2}
        assert len(user_set) == 1

    def test_user_types(self):
        """Test different user types."""
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password="hash",
            user_type=UserTypeEnum.ADMIN,
        )
        user = User(
            username="user",
            email="user@example.com",
            hashed_password="hash",
            user_type=UserTypeEnum.USER,
        )
        guest = User(
            username="guest",
            email="guest@example.com",
            hashed_password="hash",
            user_type=UserTypeEnum.GUEST,
        )

        assert admin.user_type == UserTypeEnum.ADMIN
        assert user.user_type == UserTypeEnum.USER
        assert guest.user_type == UserTypeEnum.GUEST

    def test_user_model_dump(self):
        """Test that user can be serialized to dict."""
        user = User(
            id="user-123",
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashed_password",
            user_type=UserTypeEnum.USER,
            is_active=True,
        )

        data = user.model_dump()

        assert data["id"] == "user-123"
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert data["hashed_password"] == "hashed_password"
        assert data["user_type"] == UserTypeEnum.USER
        assert data["is_active"] is True

    def test_user_from_attributes(self):
        """Test creating user from ORM model attributes."""
        # This tests the from_attributes config
        class MockORMUser:
            id = "user-123"
            username = "testuser"
            email = "test@example.com"
            full_name = "Test User"
            hashed_password = "hashed"
            user_type = UserTypeEnum.USER
            is_active = True
            is_deleted = False
            created_at = datetime.now()
            updated_at = datetime.now()

        user = User.model_validate(MockORMUser())

        assert user.id == "user-123"
        assert user.username == "testuser"
        assert user.email == "test@example.com"


class TestUserDomainEvents:
    """Test cases for User domain events."""

    def test_user_has_domain_events_list(self):
        """Test that user has domain events infrastructure."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hash",
        )

        # User should have empty domain events initially
        events = user.get_domain_events()
        assert events == []

    def test_user_can_add_domain_event(self):
        """Test that user can add domain events."""
        from domain.users.events import UserCreatedEvent

        user = User(
            id="user-123",
            username="testuser",
            email="test@example.com",
            hashed_password="hash",
        )

        event = UserCreatedEvent(
            user_id="user-123",
            username="testuser",
            email="test@example.com",
        )
        user._add_domain_event(event)

        events = user.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], UserCreatedEvent)
        assert events[0].user_id == "user-123"

    def test_user_can_clear_domain_events(self):
        """Test that user can clear domain events."""
        from domain.users.events import UserCreatedEvent

        user = User(
            id="user-123",
            username="testuser",
            email="test@example.com",
            hashed_password="hash",
        )

        event = UserCreatedEvent(
            user_id="user-123",
            username="testuser",
            email="test@example.com",
        )
        user._add_domain_event(event)
        user.clear_domain_events()

        events = user.get_domain_events()
        assert events == []


class TestUserValidation:
    """Test cases for User field validation."""

    def test_user_requires_username(self):
        """Test that username is required."""
        with pytest.raises(ValidationError):
            User(
                email="test@example.com",
                hashed_password="hash",
            )

    def test_user_requires_email(self):
        """Test that email is required."""
        with pytest.raises(ValidationError):
            User(
                username="testuser",
                hashed_password="hash",
            )

    def test_user_requires_hashed_password(self):
        """Test that hashed_password is required."""
        with pytest.raises(ValidationError):
            User(
                username="testuser",
                email="test@example.com",
            )

    def test_user_forbids_extra_fields(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError):
            User(
                username="testuser",
                email="test@example.com",
                hashed_password="hash",
                extra_field="not_allowed",
            )

