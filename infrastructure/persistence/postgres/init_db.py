from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel

from infrastructure.config import settings

# 异步引擎
async_engine: AsyncEngine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI.replace("postgresql://", "postgresql+asyncpg://"),
    echo=True,
    future=True
)

# 同步引擎（用于迁移等）
sync_engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, echo=True, future=True)

async def init_db():
    """异步初始化数据库"""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

def init_db_sync():
    """同步初始化数据库（用于迁移等）"""
    SQLModel.metadata.create_all(sync_engine)
