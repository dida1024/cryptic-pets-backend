"""
依赖注入模块
提供应用程序的各种依赖项
"""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from application.users.handlers import UserService
from infrastructure.persistence.postgres.init_db import async_engine
from infrastructure.persistence.postgres.mappers.user_mapper import UserMapper
from infrastructure.persistence.postgres.repositories.user_repository_impl import (
    PostgreSQLUserRepositoryImpl,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async with AsyncSession(async_engine) as session:
        yield session


# 数据库相关依赖
async def get_user_mapper() -> UserMapper:
    """获取用户映射器实例"""
    return UserMapper()


async def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
    mapper: UserMapper = Depends(get_user_mapper),
) -> PostgreSQLUserRepositoryImpl:
    """获取用户仓储实例"""
    return PostgreSQLUserRepositoryImpl(session, mapper)


async def get_user_service(
    user_repository: PostgreSQLUserRepositoryImpl = Depends(get_user_repository),
) -> UserService:
    """获取用户服务实例"""
    return UserService(user_repository)


# 可以添加其他服务的依赖函数
# async def get_auth_service(
#     user_service: UserService = Depends(get_user_service),
# ) -> AuthService:
#     """获取认证服务实例"""
#     return AuthService(user_service)

# async def get_notification_service() -> NotificationService:
#     """获取通知服务实例"""
#     return NotificationService()
