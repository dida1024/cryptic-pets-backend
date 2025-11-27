"""Bcrypt password hasher implementation."""

from passlib.context import CryptContext


class BcryptPasswordHasher:
    """Bcrypt implementation of PasswordHasher protocol.

    This class implements the PasswordHasher protocol using bcrypt
    through passlib's CryptContext.
    """

    def __init__(
        self,
        schemes: list[str] | None = None,
        deprecated: str = "auto",
    ):
        """Initialize the password hasher.

        Args:
            schemes: List of hashing schemes to use. Defaults to ["bcrypt"].
            deprecated: Deprecated scheme handling. Defaults to "auto".
        """
        if schemes is None:
            schemes = ["bcrypt"]
        self._context = CryptContext(schemes=schemes, deprecated=deprecated)

    def hash(self, password: str) -> str:
        """Hash a plain text password using bcrypt.

        Args:
            password: The plain text password to hash.

        Returns:
            The hashed password string.
        """
        return self._context.hash(password)

    def verify(self, password: str, hashed: str) -> bool:
        """Verify a password against a bcrypt hash.

        Args:
            password: The plain text password to verify.
            hashed: The hashed password to compare against.

        Returns:
            True if the password matches the hash, False otherwise.
        """
        return self._context.verify(password, hashed)

    def needs_rehash(self, hashed: str) -> bool:
        """Check if a hash needs to be updated.

        This can happen when the hashing algorithm is deprecated
        or when the configuration changes.

        Args:
            hashed: The hashed password to check.

        Returns:
            True if the hash should be regenerated, False otherwise.
        """
        return self._context.needs_update(hashed)

