
from pydantic import Field

from domain.base_entity import BaseEntity
from domain.users.value_objects import UserTypeEnum


class User(BaseEntity):
    """User entity representing a user in the system."""

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
