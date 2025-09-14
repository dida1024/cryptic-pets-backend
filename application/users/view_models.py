"""
用户视图模型
用于CQRS模式的查询响应
"""

from datetime import datetime

from pydantic import BaseModel

from domain.users.entities import User
from domain.users.value_objects import UserTypeEnum


class UserSummaryView(BaseModel):
    """用户摘要视图"""
    id: str
    username: str
    email: str
    full_name: str | None = None
    user_type: UserTypeEnum
    is_active: bool
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    @classmethod
    def from_entity(cls, user: User) -> "UserSummaryView":
        """从用户实体创建摘要视图"""
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            user_type=user.user_type,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            is_deleted=user.is_deleted,
        )


class UserDetailsView(BaseModel):
    """用户详情视图"""
    id: str
    username: str
    email: str
    full_name: str | None = None
    user_type: UserTypeEnum
    is_active: bool
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    # 注意：不包含密码等敏感信息

    @classmethod
    def from_entity(cls, user: User) -> "UserDetailsView":
        """从用户实体创建详情视图"""
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            user_type=user.user_type,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            is_deleted=user.is_deleted,
        )


class UserSearchResult(BaseModel):
    """用户搜索结果"""
    users: list[UserSummaryView]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(
        cls,
        users: list[UserSummaryView],
        total: int,
        page: int,
        page_size: int,
    ) -> "UserSearchResult":
        """创建搜索结果"""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            users=users,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


class UserProfileView(BaseModel):
    """用户资料视图（扩展信息）"""
    user_id: str
    bio: str | None = None
    avatar_url: str | None = None
    location: str | None = None
    website: str | None = None
    # 可以添加更多用户资料字段

    @classmethod
    def from_entity(cls, user: User) -> "UserProfileView":
        """从用户实体创建资料视图"""
        # 目前用户实体没有这些字段，返回基础信息
        return cls(
            user_id=user.id,
            bio=None,
            avatar_url=None,
            location=None,
            website=None,
        )
