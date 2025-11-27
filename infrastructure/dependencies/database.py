"""Database dependency module.

Provides database session and engine dependencies.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.persistence.postgres.init_db import async_engine


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session with automatic transaction management.

    Yields:
        AsyncSession: Database session with transaction started.
        Transaction is automatically committed on success or rolled back on error.
    """
    async with AsyncSession(async_engine, expire_on_commit=False) as session:
        async with session.begin():
            yield session

