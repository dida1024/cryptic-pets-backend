"""Security dependency module.

Provides password hashing and policy dependencies.
"""

from domain.users.services import PasswordHasher, PasswordPolicy
from infrastructure.security.bcrypt_hasher import BcryptPasswordHasher


def get_password_hasher() -> PasswordHasher:
    """Get password hasher instance.

    Returns:
        PasswordHasher: Bcrypt password hasher implementation.
    """
    return BcryptPasswordHasher()


def get_password_policy() -> PasswordPolicy:
    """Get password policy instance.

    Returns:
        PasswordPolicy: Default password policy with standard requirements.
    """
    return PasswordPolicy()

