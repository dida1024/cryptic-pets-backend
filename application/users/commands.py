
from pydantic import BaseModel, EmailStr

from domain.users.value_objects import UserTypeEnum


class CreateUserCommand(BaseModel):
    """创建用户命令"""
    username: str
    email: EmailStr
    password: str
    full_name: str | None = None
    user_type: UserTypeEnum = UserTypeEnum.USER
    is_active: bool = True


class UpdateUserCommand(BaseModel):
    """更新用户命令"""
    user_id: str
    username: str | None = None
    email: EmailStr | None = None
    full_name: str | None = None
    user_type: UserTypeEnum | None = None
    is_active: bool | None = None


class UpdatePasswordCommand(BaseModel):
    """更新密码命令"""
    user_id: str
    current_password: str
    new_password: str


class DeleteUserCommand(BaseModel):
    """删除用户命令"""
    user_id: str


class ListUsersQuery(BaseModel):
    """用户列表查询"""
    page: int = 1
    page_size: int = 10
    search: str | None = None
    user_type: UserTypeEnum | None = None
    is_active: bool | None = None
    include_deleted: bool = False
