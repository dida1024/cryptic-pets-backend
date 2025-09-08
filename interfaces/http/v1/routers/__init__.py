from fastapi import APIRouter

from .breed import router as breed_router
from .pet import router as pet_router
from .user import router as user_router

api_router = APIRouter()

# 注册路由
api_router.include_router(user_router)
api_router.include_router(pet_router)
api_router.include_router(breed_router)
