"""End-to-end test configuration and fixtures."""

from collections.abc import AsyncGenerator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from main import app

# Use SQLite for e2e tests (in-memory)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Configure anyio to use asyncio backend."""
    return "asyncio"


@pytest.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def api_v1_prefix() -> str:
    """Get the API v1 prefix."""
    return "/api/v1"


@pytest.fixture
def user_payload() -> dict[str, Any]:
    """Create a sample user payload for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123",
        "full_name": "Test User",
    }


@pytest.fixture
def pet_payload() -> dict[str, Any]:
    """Create a sample pet payload for testing."""
    return {
        "name": "Fluffy",
        "description": "A lovely corn snake",
        "owner_id": "user-123",
        "breed_id": "breed-123",
        "gender": "UNKNOWN",
    }

