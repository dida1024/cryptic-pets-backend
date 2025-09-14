"""
用户查询模型
实现CQRS模式的查询部分
"""

from pydantic import BaseModel, Field

from domain.users.value_objects import UserTypeEnum


class GetUserByIdQuery(BaseModel):
    """根据ID获取用户查询"""
    user_id: str
    include_profile: bool = Field(default=False, description="是否包含详细资料信息")


class GetUserByUsernameQuery(BaseModel):
    """根据用户名获取用户查询"""
    username: str
    include_profile: bool = Field(default=False, description="是否包含详细资料信息")


class GetUserByEmailQuery(BaseModel):
    """根据邮箱获取用户查询"""
    email: str
    include_profile: bool = Field(default=False, description="是否包含详细资料信息")


class SearchUsersQuery(BaseModel):
    """搜索用户查询"""
    search_term: str | None = Field(default=None, description="搜索关键词（用户名或邮箱）")
    user_type: UserTypeEnum | None = Field(default=None, description="用户类型过滤")
    is_active: bool | None = Field(default=None, description="激活状态过滤")
    page: int = Field(default=1, description="页码，从1开始")
    page_size: int = Field(default=10, description="每页大小")
    include_deleted: bool = Field(default=False, description="是否包含已删除的用户")


class ListUsersQuery(BaseModel):
    """用户列表查询（保持向后兼容）"""
    page: int = Field(default=1, description="页码，从1开始")
    page_size: int = Field(default=10, description="每页大小")
    search: str | None = Field(default=None, description="搜索关键词（用户名或邮箱）")
    user_type: UserTypeEnum | None = Field(default=None, description="用户类型过滤")
    is_active: bool | None = Field(default=None, description="激活状态过滤")
    include_deleted: bool = Field(default=False, description="是否包含已删除的用户")
