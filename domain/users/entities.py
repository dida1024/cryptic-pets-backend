"""User entity with rich domain behavior."""

from typing import TYPE_CHECKING

from pydantic import Field

from domain.common.aggregate_root import AggregateRoot
from domain.users.value_objects import UserTypeEnum

if TYPE_CHECKING:
    from domain.users.services import PasswordHasher


class User(AggregateRoot):
    """User entity representing a user in the system.

    This is an aggregate root that encapsulates user-related business logic.
    """

    username: str = Field(..., description="Unique username of the user")
    email: str = Field(..., description="Unique email address of the user")
    full_name: str | None = Field(default=None, description="Full name of the user")
    hashed_password: str = Field(..., description="Hashed password of the user")
    user_type: UserTypeEnum = Field(
        default=UserTypeEnum.USER, description="Type of user (admin, user, guest)"
    )
    is_active: bool = Field(
        default=True, description="Indicates if the user account is active"
    )

    # ========== Business Methods ==========

    def verify_password(self, plain_password: str, hasher: "PasswordHasher") -> bool:
        """Verify a plain password against the stored hash.

        Args:
            plain_password: The plain text password to verify.
            hasher: The password hasher implementation.

        Returns:
            True if the password is correct, False otherwise.
        """
        return hasher.verify(plain_password, self.hashed_password)

    def change_password(
        self,
        new_password: str,
        hasher: "PasswordHasher",
    ) -> None:
        """Change the user's password.

        Args:
            new_password: The new plain text password.
            hasher: The password hasher implementation.

        Emits:
            UserPasswordChangedEvent: When password is successfully changed.
        """
        self.hashed_password = hasher.hash(new_password)
        self._update_timestamp()

        from domain.users.events import UserPasswordChangedEvent

        self.add_domain_event(
            UserPasswordChangedEvent(
                user_id=self.id,
            )
        )

    def deactivate(self) -> None:
        """Deactivate the user account.

        Emits:
            UserDeactivatedEvent: When user is deactivated.
        """
        if not self.is_active:
            return  # Already deactivated, no-op

        self.is_active = False
        self._update_timestamp()

        from domain.users.events import UserDeactivatedEvent

        self.add_domain_event(
            UserDeactivatedEvent(
                user_id=self.id,
                username=self.username,
            )
        )

    def activate(self) -> None:
        """Activate the user account.

        Emits:
            UserActivatedEvent: When user is activated.
        """
        if self.is_active:
            return  # Already active, no-op

        self.is_active = True
        self._update_timestamp()

        from domain.users.events import UserActivatedEvent

        self.add_domain_event(
            UserActivatedEvent(
                user_id=self.id,
                username=self.username,
            )
        )

    def promote_to_admin(self, promoted_by: str | None = None) -> None:
        """Promote the user to admin role.

        Args:
            promoted_by: The ID of the user who performed the promotion.

        Emits:
            UserPromotedEvent: When user is promoted to admin.
        """
        if self.user_type == UserTypeEnum.ADMIN:
            return  # Already admin, no-op

        old_user_type = self.user_type
        self.user_type = UserTypeEnum.ADMIN
        self._update_timestamp()

        from domain.users.events import UserPromotedEvent

        self.add_domain_event(
            UserPromotedEvent(
                user_id=self.id,
                username=self.username,
                old_user_type=old_user_type.value,
                new_user_type=self.user_type.value,
                promoted_by=promoted_by,
            )
        )

    def demote_to_user(self) -> None:
        """Demote the user from admin to regular user.

        Emits:
            UserDemotedEvent: When user is demoted from admin.
        """
        if self.user_type == UserTypeEnum.USER:
            return  # Already regular user, no-op

        old_user_type = self.user_type
        self.user_type = UserTypeEnum.USER
        self._update_timestamp()

        from domain.users.events import UserDemotedEvent

        self.add_domain_event(
            UserDemotedEvent(
                user_id=self.id,
                username=self.username,
                old_user_type=old_user_type.value,
                new_user_type=self.user_type.value,
            )
        )

    def update_profile(
        self,
        full_name: str | None = None,
        email: str | None = None,
    ) -> list[str]:
        """Update the user's profile information.

        Args:
            full_name: The new full name (optional).
            email: The new email address (optional).

        Returns:
            List of fields that were updated.

        Emits:
            UserUpdatedEvent: When profile is updated.
        """
        updated_fields: list[str] = []

        if full_name is not None and full_name != self.full_name:
            self.full_name = full_name
            updated_fields.append("full_name")

        if email is not None and email != self.email:
            self.email = email
            updated_fields.append("email")

        if updated_fields:
            self._update_timestamp()

            from domain.users.events import UserUpdatedEvent

            self.add_domain_event(
                UserUpdatedEvent(
                    user_id=self.id,
                    updated_fields=updated_fields,
                )
            )

        return updated_fields

    def update_username(self, new_username: str) -> None:
        """Update the user's username.

        Args:
            new_username: The new username.

        Emits:
            UserUpdatedEvent: When username is updated.
        """
        if new_username == self.username:
            return  # No change

        self.username = new_username
        self._update_timestamp()

        from domain.users.events import UserUpdatedEvent

        self.add_domain_event(
            UserUpdatedEvent(
                user_id=self.id,
                updated_fields=["username"],
            )
        )

    def change_user_type(self, new_user_type: UserTypeEnum) -> None:
        """Change the user's type.

        Args:
            new_user_type: The new user type.

        Emits:
            UserUpdatedEvent: When user type is changed.
        """
        if new_user_type == self.user_type:
            return  # No change

        self.user_type = new_user_type
        self._update_timestamp()

        from domain.users.events import UserUpdatedEvent

        self.add_domain_event(
            UserUpdatedEvent(
                user_id=self.id,
                updated_fields=["user_type"],
            )
        )

    # ========== Query Methods ==========

    def is_admin(self) -> bool:
        """Check if the user is an admin."""
        return self.user_type == UserTypeEnum.ADMIN

    def is_guest(self) -> bool:
        """Check if the user is a guest."""
        return self.user_type == UserTypeEnum.GUEST

    def can_login(self) -> bool:
        """Check if the user can log in.

        Returns:
            True if the user is active and not deleted.
        """
        return self.is_active and not self.is_deleted
