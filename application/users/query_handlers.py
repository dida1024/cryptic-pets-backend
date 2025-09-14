"""
用户查询处理器
实现CQRS模式的查询部分
"""

from loguru import logger

from application.users.queries import (
    GetUserByEmailQuery,
    GetUserByIdQuery,
    GetUserByUsernameQuery,
    ListUsersQuery,
    SearchUsersQuery,
)
from application.users.view_models import (
    UserDetailsView,
    UserSearchResult,
    UserSummaryView,
)
from domain.users.exceptions import UserNotFoundError
from domain.users.repository import UserRepository


class UserQueryService:
    """用户查询服务 - 专门处理读操作"""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.logger = logger

    async def get_user_details(self, query: GetUserByIdQuery) -> UserDetailsView:
        """获取用户详情"""
        # 获取用户
        user = await self.user_repository.get_by_id(query.user_id)
        if not user:
            raise UserNotFoundError(f"User with id '{query.user_id}' not found")

        # 创建详情视图
        user_view = UserDetailsView.from_entity(user)

        # 如果需要包含资料信息
        if query.include_profile:
            # 这里可以添加更多资料信息的加载逻辑
            # 目前用户实体没有扩展资料字段，所以暂时不实现
            pass

        return user_view

    async def get_user_by_username(self, query: GetUserByUsernameQuery) -> UserDetailsView:
        """根据用户名获取用户"""
        # 获取用户
        user = await self.user_repository.get_by_username(query.username)
        if not user:
            raise UserNotFoundError(f"User with username '{query.username}' not found")

        # 创建详情查询
        detail_query = GetUserByIdQuery(
            user_id=user.id,
            include_profile=query.include_profile,
        )

        # 使用详情查询处理器
        return await self.get_user_details(detail_query)

    async def get_user_by_email(self, query: GetUserByEmailQuery) -> UserDetailsView:
        """根据邮箱获取用户"""
        # 获取用户
        user = await self.user_repository.get_by_email(query.email)
        if not user:
            raise UserNotFoundError(f"User with email '{query.email}' not found")

        # 创建详情查询
        detail_query = GetUserByIdQuery(
            user_id=user.id,
            include_profile=query.include_profile,
        )

        # 使用详情查询处理器
        return await self.get_user_details(detail_query)

    async def search_users(self, query: SearchUsersQuery) -> UserSearchResult:
        """搜索用户"""
        # 搜索用户
        users, total_count = await self.user_repository.list_all(
            page=query.page,
            page_size=query.page_size,
            search=query.search_term,
            user_type=query.user_type.value if query.user_type else None,
            is_active=query.is_active,
            include_deleted=query.include_deleted,
        )

        # 创建摘要视图模型
        user_views = [UserSummaryView.from_entity(user) for user in users]

        # 创建搜索结果
        return UserSearchResult.create(
            users=user_views,
            total=total_count,
            page=query.page,
            page_size=query.page_size,
        )

    async def list_users(self, query: ListUsersQuery) -> UserSearchResult:
        """获取用户列表（保持向后兼容）"""
        # 搜索用户
        users, total_count = await self.user_repository.list_all(
            page=query.page,
            page_size=query.page_size,
            search=query.search,
            user_type=query.user_type.value if query.user_type else None,
            is_active=query.is_active,
            include_deleted=query.include_deleted,
        )

        # 创建摘要视图模型
        user_views = [UserSummaryView.from_entity(user) for user in users]

        # 创建搜索结果
        return UserSearchResult.create(
            users=user_views,
            total=total_count,
            page=query.page,
            page_size=query.page_size,
        )
