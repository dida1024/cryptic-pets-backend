"""Pytest configuration and fixtures."""

import asyncio
from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import Field

from domain.common.events import DomainEvent, EventBus
from domain.pets.entities import Pet
from domain.pets.value_objects import GenderEnum
from domain.users.entities import User
from domain.users.value_objects import UserTypeEnum


# Configure pytest-anyio to use asyncio
@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Configure anyio to use asyncio backend."""
    return "asyncio"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============ Domain Fixtures ============


@pytest.fixture
def sample_user() -> User:
    """Create a sample user entity for testing."""
    return User(
        id="user-123",
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed_password_123",
        user_type=UserTypeEnum.USER,
        is_active=True,
    )


@pytest.fixture
def sample_admin_user() -> User:
    """Create a sample admin user entity for testing."""
    return User(
        id="admin-123",
        username="adminuser",
        email="admin@example.com",
        full_name="Admin User",
        hashed_password="hashed_password_456",
        user_type=UserTypeEnum.ADMIN,
        is_active=True,
    )


@pytest.fixture
def sample_pet() -> Pet:
    """Create a sample pet entity for testing."""
    return Pet(
        id="pet-123",
        name="Fluffy",
        description="A lovely corn snake",
        owner_id="user-123",
        breed_id="breed-123",
        gender=GenderEnum.MALE,
    )


@pytest.fixture
def sample_pet_female() -> Pet:
    """Create a sample female pet entity for testing."""
    return Pet(
        id="pet-456",
        name="Sunny",
        description="A beautiful female corn snake",
        owner_id="user-123",
        breed_id="breed-123",
        gender=GenderEnum.FEMALE,
    )


# ============ Mock Fixtures ============


@pytest.fixture
def mock_user_repository() -> MagicMock:
    """Create a mock user repository."""
    mock = MagicMock()
    mock.get_by_id = AsyncMock(return_value=None)
    mock.get_by_username = AsyncMock(return_value=None)
    mock.get_by_email = AsyncMock(return_value=None)
    mock.exists_by_username = AsyncMock(return_value=False)
    mock.exists_by_email = AsyncMock(return_value=False)
    mock.create = AsyncMock()
    mock.update = AsyncMock()
    mock.delete = AsyncMock(return_value=True)
    mock.list_all = AsyncMock(return_value=([], 0))
    return mock


@pytest.fixture
def mock_pet_repository() -> MagicMock:
    """Create a mock pet repository."""
    mock = MagicMock()
    mock.get_by_id = AsyncMock(return_value=None)
    mock.get_by_owner_id = AsyncMock(return_value=[])
    mock.get_by_breed_id = AsyncMock(return_value=[])
    mock.get_by_morphology_id = AsyncMock(return_value=[])
    mock.exists_by_name = AsyncMock(return_value=False)
    mock.create = AsyncMock()
    mock.update = AsyncMock()
    mock.delete = AsyncMock(return_value=True)
    mock.list_all = AsyncMock(return_value=([], 0))
    return mock


@pytest.fixture
def mock_breed_repository() -> MagicMock:
    """Create a mock breed repository."""
    mock = MagicMock()
    mock.get_by_id = AsyncMock(return_value=None)
    mock.get_by_name = AsyncMock(return_value=None)
    mock.create = AsyncMock()
    mock.update = AsyncMock()
    mock.delete = AsyncMock(return_value=True)
    mock.list_all = AsyncMock(return_value=([], 0))
    return mock


@pytest.fixture
def mock_morphology_repository() -> MagicMock:
    """Create a mock morphology repository."""
    mock = MagicMock()
    mock.get_by_id = AsyncMock(return_value=None)
    mock.is_compatible_with_breed = AsyncMock(return_value=True)
    mock.create = AsyncMock()
    mock.update = AsyncMock()
    mock.delete = AsyncMock(return_value=True)
    mock.list_all = AsyncMock(return_value=([], 0))
    return mock


@pytest.fixture
def mock_event_bus() -> EventBus:
    """Create a mock event bus for testing."""
    event_bus = EventBus()
    event_bus.publish = AsyncMock()
    event_bus.publish_all = AsyncMock()
    return event_bus


# ============ Test Event Classes ============


class TestDomainEvent(DomainEvent):
    """A test domain event for testing purposes."""

    message: str = Field(default="test")
    entity_id: str = Field(default="test-id")


@pytest.fixture
def test_event() -> TestDomainEvent:
    """Create a test domain event."""
    return TestDomainEvent(message="Test event", entity_id="entity-123")


# ============ Helper Functions ============


def create_user(
    id: str = "user-123",
    username: str = "testuser",
    email: str = "test@example.com",
    full_name: str = "Test User",
    hashed_password: str = "hashed_password",
    user_type: UserTypeEnum = UserTypeEnum.USER,
    is_active: bool = True,
) -> User:
    """Helper function to create a user with custom attributes."""
    return User(
        id=id,
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
        user_type=user_type,
        is_active=is_active,
    )


def create_pet(
    id: str = "pet-123",
    name: str = "Fluffy",
    description: str | None = "A lovely pet",
    owner_id: str = "user-123",
    breed_id: str = "breed-123",
    gender: GenderEnum = GenderEnum.UNKNOWN,
    morphology_id: str | None = None,
) -> Pet:
    """Helper function to create a pet with custom attributes."""
    return Pet(
        id=id,
        name=name,
        description=description,
        owner_id=owner_id,
        breed_id=breed_id,
        gender=gender,
        morphology_id=morphology_id,
    )

