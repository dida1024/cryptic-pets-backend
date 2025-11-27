"""User command handlers.

Implements the CQRS pattern's command part, handling write operations.
Uses domain services and entity methods instead of implementing business logic directly.
"""

from uuid import uuid4

from loguru import logger

from application.users.commands import (
    CreateUserCommand,
    DeleteUserCommand,
    UpdatePasswordCommand,
    UpdateUserCommand,
)
from domain.users.entities import User
from domain.users.events import UserCreatedEvent
from domain.users.exceptions import (
    DuplicateEmailError,
    DuplicateUsernameError,
    InvalidCredentialsError,
    UserNotFoundError,
)
from domain.users.repository import UserRepository
from domain.users.services import PasswordHasher, PasswordPolicy


class CreateUserHandler:
    """Create user command handler."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        password_policy: PasswordPolicy | None = None,
    ):
        """Initialize the handler.

        Args:
            user_repository: Repository for user persistence.
            password_hasher: Password hashing service.
            password_policy: Optional password policy for validation.
        """
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.password_policy = password_policy or PasswordPolicy()
        self.logger = logger

    async def handle(self, command: CreateUserCommand) -> User:
        """Handle create user command.

        Args:
            command: The create user command.

        Returns:
            The created user entity.

        Raises:
            DuplicateUsernameError: If username already exists.
            DuplicateEmailError: If email already exists.
            WeakPasswordError: If password doesn't meet policy requirements.
        """
        # Validate password strength
        self.password_policy.validate(command.password)

        # Check if username already exists
        if await self.user_repository.exists_by_username(command.username):
            raise DuplicateUsernameError(f"Username '{command.username}' already exists")

        # Check if email already exists
        if await self.user_repository.exists_by_email(command.email):
            raise DuplicateEmailError(f"Email '{command.email}' already exists")

        # Hash the password using the injected hasher
        hashed_password = self.password_hasher.hash(command.password)

        # Create user entity
        user = User(
            username=command.username,
            email=command.email,
            full_name=command.full_name,
            hashed_password=hashed_password,
            user_type=command.user_type,
            is_active=command.is_active,
        )
        if not user.id:
            user.id = str(uuid4())

        self.logger.info(f"Creating user: {user.username}")

        # Add domain event (before persistence, so repository can publish)
        user.add_domain_event(
            UserCreatedEvent(
                user_id=user.id,
                username=user.username,
                email=user.email,
            )
        )

        # Save user (repository is responsible for publishing domain events)
        return await self.user_repository.create(user)


class UpdateUserHandler:
    """Update user command handler."""

    def __init__(self, user_repository: UserRepository):
        """Initialize the handler.

        Args:
            user_repository: Repository for user persistence.
        """
        self.user_repository = user_repository
        self.logger = logger

    async def handle(self, command: UpdateUserCommand) -> User:
        """Handle update user command.

        Args:
            command: The update user command.

        Returns:
            The updated user entity.

        Raises:
            UserNotFoundError: If user is not found.
            DuplicateUsernameError: If new username already exists.
            DuplicateEmailError: If new email already exists.
        """
        # Get existing user
        if not (user := await self.user_repository.get_by_id(command.user_id)):
            raise UserNotFoundError(f"User with id '{command.user_id}' not found")

        # Check username uniqueness
        if command.username and command.username != user.username:
            if await self.user_repository.exists_by_username(
                command.username, exclude_id=user.id
            ):
                raise DuplicateUsernameError(
                    f"Username '{command.username}' already exists"
                )

        # Check email uniqueness
        if command.email and command.email != user.email:
            if await self.user_repository.exists_by_email(
                command.email, exclude_id=user.id
            ):
                raise DuplicateEmailError(f"Email '{command.email}' already exists")

        # Use entity methods to update fields
        if command.username is not None and command.username != user.username:
            user.update_username(command.username)

        if command.email is not None or command.full_name is not None:
            user.update_profile(
                full_name=command.full_name,
                email=command.email,
            )

        if command.user_type is not None and command.user_type != user.user_type:
            user.change_user_type(command.user_type)

        if command.is_active is not None:
            if command.is_active and not user.is_active:
                user.activate()
            elif not command.is_active and user.is_active:
                user.deactivate()

        self.logger.info(f"Updating user: {user.username}")

        return await self.user_repository.update(user)


class UpdatePasswordHandler:
    """Update password command handler."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        password_policy: PasswordPolicy | None = None,
    ):
        """Initialize the handler.

        Args:
            user_repository: Repository for user persistence.
            password_hasher: Password hashing service.
            password_policy: Optional password policy for validation.
        """
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.password_policy = password_policy or PasswordPolicy()
        self.logger = logger

    async def handle(self, command: UpdatePasswordCommand) -> User:
        """Handle update password command.

        Args:
            command: The update password command.

        Returns:
            The updated user entity.

        Raises:
            UserNotFoundError: If user is not found.
            InvalidCredentialsError: If current password is incorrect.
            WeakPasswordError: If new password doesn't meet policy requirements.
        """
        # Get existing user
        user = await self.user_repository.get_by_id(command.user_id)
        if not user:
            raise UserNotFoundError(f"User with id '{command.user_id}' not found")

        # Verify current password using entity method
        if not user.verify_password(command.current_password, self.password_hasher):
            raise InvalidCredentialsError("Current password is incorrect")

        # Validate new password strength
        self.password_policy.validate(command.new_password)

        # Use entity method to change password (handles hashing and event)
        user.change_password(command.new_password, self.password_hasher)

        self.logger.info(f"Updating password for user: {user.username}")

        return await self.user_repository.update(user)


class DeleteUserHandler:
    """Delete user command handler."""

    def __init__(self, user_repository: UserRepository):
        """Initialize the handler.

        Args:
            user_repository: Repository for user persistence.
        """
        self.user_repository = user_repository
        self.logger = logger

    async def handle(self, command: DeleteUserCommand) -> bool:
        """Handle delete user command.

        Args:
            command: The delete user command.

        Returns:
            True if user was deleted.

        Raises:
            UserNotFoundError: If user is not found.
        """
        # Check if user exists
        user = await self.user_repository.get_by_id(command.user_id)
        if not user:
            raise UserNotFoundError(f"User with id '{command.user_id}' not found")

        self.logger.info(f"Deleting user: {user.username}")

        # Use entity method for soft delete and domain event
        from domain.users.events import UserDeletedEvent

        user.mark_as_deleted()
        user.add_domain_event(
            UserDeletedEvent(
                user_id=user.id,
                username=user.username,
            )
        )

        # Repository is responsible for executing soft delete and publishing events
        return await self.user_repository.delete(user)
