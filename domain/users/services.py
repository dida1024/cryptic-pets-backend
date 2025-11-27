"""User domain services.

This module contains domain services and protocols for the users domain.
"""

import re
from typing import Protocol

from pydantic import BaseModel, Field

from domain.users.exceptions import WeakPasswordError


class PasswordHasher(Protocol):
    """Protocol for password hashing operations.

    This protocol defines the interface for password hashing implementations.
    The actual implementation (e.g., bcrypt) should be in the infrastructure layer.
    """

    def hash(self, password: str) -> str:
        """Hash a plain text password.

        Args:
            password: The plain text password to hash.

        Returns:
            The hashed password string.
        """
        ...

    def verify(self, password: str, hashed: str) -> bool:
        """Verify a password against a hash.

        Args:
            password: The plain text password to verify.
            hashed: The hashed password to compare against.

        Returns:
            True if the password matches the hash, False otherwise.
        """
        ...


class PasswordPolicy(BaseModel):
    """Password policy for validating password strength.

    This domain service encapsulates the business rules for password validation.
    """

    min_length: int = Field(default=8, description="Minimum password length")
    max_length: int = Field(default=128, description="Maximum password length")
    require_uppercase: bool = Field(default=True, description="Require uppercase letter")
    require_lowercase: bool = Field(default=True, description="Require lowercase letter")
    require_digit: bool = Field(default=True, description="Require digit")
    require_special: bool = Field(default=False, description="Require special character")
    special_characters: str = Field(
        default="!@#$%^&*()_+-=[]{}|;:,.<>?",
        description="Allowed special characters",
    )

    def validate(self, password: str) -> None:
        """Validate a password against the policy.

        Args:
            password: The password to validate.

        Raises:
            WeakPasswordError: If the password does not meet the policy requirements.
        """
        errors: list[str] = []

        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long")

        if len(password) > self.max_length:
            errors.append(f"Password must not exceed {self.max_length} characters")

        if self.require_uppercase and not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")

        if self.require_lowercase and not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")

        if self.require_digit and not re.search(r"\d", password):
            errors.append("Password must contain at least one digit")

        if self.require_special:
            escaped_special = re.escape(self.special_characters)
            if not re.search(f"[{escaped_special}]", password):
                errors.append("Password must contain at least one special character")

        if errors:
            raise WeakPasswordError("; ".join(errors))

    def is_valid(self, password: str) -> bool:
        """Check if a password is valid without raising an exception.

        Args:
            password: The password to validate.

        Returns:
            True if the password is valid, False otherwise.
        """
        try:
            self.validate(password)
            return True
        except WeakPasswordError:
            return False

