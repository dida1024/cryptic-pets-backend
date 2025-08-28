"""
认证相关的路由
演示如何复用依赖
"""

from fastapi import APIRouter, Depends

from application.users.handlers import UserService
from infrastructure.dependencies import get_user_service

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login")
async def login(
    user_service: UserService = Depends(get_user_service),
):
    """用户登录"""
    # 这里可以使用 user_service 进行用户验证
    # 例如: user = await user_service.get_user_by_username(username)
    pass


@router.post("/register")
async def register(
    user_service: UserService = Depends(get_user_service),
):
    """用户注册"""
    # 这里可以使用 user_service 创建新用户
    # 例如: user = await user_service.create_user(command)
    pass
