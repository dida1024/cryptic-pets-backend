

from sqlmodel import Field

from domain.users.value_objects import UserTypeEnum
from infrastructure.persistence.postgres.models.base import BaseModel


class UserModel(BaseModel, table=True):
    __tablename__ = "users"

    username: str = Field(index=True, nullable=False, unique=True)
    email: str = Field(index=True, nullable=False, unique=True)
    full_name: str | None = Field(default=None, nullable=True)
    hashed_password: str = Field(nullable=False)
    user_type: UserTypeEnum = Field(default=UserTypeEnum.USER, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
