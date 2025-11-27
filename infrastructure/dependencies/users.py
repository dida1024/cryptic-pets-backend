"""User dependency module.

Provides user-related command handlers and query services.
"""

from fastapi import Depends

from application.users.command_handlers import (
    CreateUserHandler,
    DeleteUserHandler,
    UpdatePasswordHandler,
    UpdateUserHandler,
)
from application.users.query_handlers import UserQueryService
from domain.users.services import PasswordHasher, PasswordPolicy
from infrastructure.dependencies.repositories import get_user_repository
from infrastructure.dependencies.security import (
    get_password_hasher,
    get_password_policy,
)
from infrastructure.persistence.postgres.repositories.user_repository_impl import (
    PostgreSQLUserRepositoryImpl,
)


async def get_create_user_handler(
    user_repository: PostgreSQLUserRepositoryImpl = Depends(get_user_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    password_policy: PasswordPolicy = Depends(get_password_policy),
) -> CreateUserHandler:
    """Get create user command handler instance.

    Args:
        user_repository: User repository.
        password_hasher: Password hasher service.
        password_policy: Password policy service.

    Returns:
        CreateUserHandler: Handler for creating users.
    """
    return CreateUserHandler(user_repository, password_hasher, password_policy)


async def get_update_user_handler(
    user_repository: PostgreSQLUserRepositoryImpl = Depends(get_user_repository),
) -> UpdateUserHandler:
    """Get update user command handler instance.

    Args:
        user_repository: User repository.

    Returns:
        UpdateUserHandler: Handler for updating users.
    """
    return UpdateUserHandler(user_repository)


async def get_update_password_handler(
    user_repository: PostgreSQLUserRepositoryImpl = Depends(get_user_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    password_policy: PasswordPolicy = Depends(get_password_policy),
) -> UpdatePasswordHandler:
    """Get update password command handler instance.

    Args:
        user_repository: User repository.
        password_hasher: Password hasher service.
        password_policy: Password policy service.

    Returns:
        UpdatePasswordHandler: Handler for updating passwords.
    """
    return UpdatePasswordHandler(user_repository, password_hasher, password_policy)


async def get_delete_user_handler(
    user_repository: PostgreSQLUserRepositoryImpl = Depends(get_user_repository),
) -> DeleteUserHandler:
    """Get delete user command handler instance.

    Args:
        user_repository: User repository.

    Returns:
        DeleteUserHandler: Handler for deleting users.
    """
    return DeleteUserHandler(user_repository)


async def get_user_query_service(
    user_repository: PostgreSQLUserRepositoryImpl = Depends(get_user_repository),
) -> UserQueryService:
    """Get user query service instance.

    Args:
        user_repository: User repository.

    Returns:
        UserQueryService: Service for querying users.
    """
    return UserQueryService(user_repository)

