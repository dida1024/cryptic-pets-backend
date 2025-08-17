from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from domain.users.value_objects import UserTypeEnum


class UserBaseSchema(BaseModel):
    """用户基础架构"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    full_name: str | None = Field(None, max_length=100, description="全名")
    user_type: UserTypeEnum = Field(default=UserTypeEnum.USER, description="用户类型")
    is_active: bool = Field(default=True, description="是否激活")


class CreateUserRequest(UserBaseSchema):
    """创建用户请求"""
    password: str = Field(..., min_length=8, max_length=100, description="密码")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "password": "strongpassword123",
                "user_type": "user",
                "is_active": True
            }
        }


class UpdateUserRequest(BaseModel):
    """更新用户请求"""
    username: str | None = Field(None, min_length=3, max_length=50, description="用户名")
    email: EmailStr | None = Field(None, description="邮箱地址")
    full_name: str | None = Field(None, max_length=100, description="全名")
    user_type: UserTypeEnum | None = Field(None, description="用户类型")
    is_active: bool | None = Field(None, description="是否激活")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe_updated",
                "email": "john.updated@example.com",
                "full_name": "John Doe Updated",
                "user_type": "user",
                "is_active": True
            }
        }


class UserResponse(UserBaseSchema):
    """用户响应"""
    id: str = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    is_deleted: bool = Field(..., description="是否删除")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "johndoe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "user_type": "user",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "is_deleted": False
            }
        }


class PasswordUpdateRequest(BaseModel):
    """密码更新请求"""
    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=8, max_length=100, description="新密码")

    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newstrongpassword123"
            }
        }


class UserListQuery(BaseModel):
    """用户列表查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")
    search: str | None = Field(None, description="搜索关键字（用户名或邮箱）")
    user_type: UserTypeEnum | None = Field(None, description="用户类型过滤")
    is_active: bool | None = Field(None, description="激活状态过滤")
    include_deleted: bool = Field(default=False, description="是否包含已删除用户")

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "page_size": 10,
                "search": "john",
                "user_type": "user",
                "is_active": True,
                "include_deleted": False
            }
        }
