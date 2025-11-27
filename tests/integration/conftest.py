"""Integration test configuration and fixtures."""

from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from domain.common.event_publisher import EventPublisher
from infrastructure.persistence.postgres.mappers.breed_mapper import BreedMapper
from infrastructure.persistence.postgres.mappers.gene_mapper import GeneMapper
from infrastructure.persistence.postgres.mappers.morph_gene_mapping_mapper import (
    MorphGeneMappingMapper,
)
from infrastructure.persistence.postgres.mappers.morphology_mapper import (
    MorphologyMapper,
)
from infrastructure.persistence.postgres.mappers.pet_mapper import PetMapper
from infrastructure.persistence.postgres.mappers.user_mapper import UserMapper

# Use SQLite for integration tests (in-memory)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Configure anyio to use asyncio backend."""
    return "asyncio"


@pytest.fixture(scope="function")
async def async_engine():
    """Create an async engine for testing."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for testing."""
    async with AsyncSession(async_engine, expire_on_commit=False) as session:
        yield session
        await session.rollback()


@pytest.fixture
def event_publisher() -> EventPublisher:
    """Create an event publisher for testing."""
    return EventPublisher()


@pytest.fixture
def user_mapper() -> UserMapper:
    """Create a user mapper."""
    return UserMapper()


@pytest.fixture
def breed_mapper() -> BreedMapper:
    """Create a breed mapper."""
    return BreedMapper()


@pytest.fixture
def gene_mapper() -> GeneMapper:
    """Create a gene mapper."""
    return GeneMapper()


@pytest.fixture
def morph_gene_mapping_mapper(gene_mapper) -> MorphGeneMappingMapper:
    """Create a morph gene mapping mapper."""
    return MorphGeneMappingMapper(gene_mapper)


@pytest.fixture
def morphology_mapper(morph_gene_mapping_mapper) -> MorphologyMapper:
    """Create a morphology mapper."""
    return MorphologyMapper(morph_gene_mapping_mapper)


@pytest.fixture
def pet_mapper(breed_mapper, morphology_mapper, morph_gene_mapping_mapper, user_mapper) -> PetMapper:
    """Create a pet mapper."""
    return PetMapper(
        breed_mapper=breed_mapper,
        morphology_mapper=morphology_mapper,
        gene_mapping_mapper=morph_gene_mapping_mapper,
        user_mapper=user_mapper,
    )

