from fastapi import APIRouter

from .user import router as user_router

api_router = APIRouter()

# 注册路由
api_router.include_router(user_router)
