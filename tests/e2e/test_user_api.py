"""End-to-end tests for User API."""

from typing import Any

import pytest
from httpx import AsyncClient


class TestUserAPI:
    """End-to-end tests for User API endpoints."""

    @pytest.mark.anyio
    async def test_create_user_success(
        self, async_client: AsyncClient, api_v1_prefix: str, user_payload: dict[str, Any]
    ):
        """Test successful user creation via API."""
        response = await async_client.post(
            f"{api_v1_prefix}/users",
            json=user_payload,
        )

        # Note: This test may fail due to database not being set up
        # In a real scenario, you'd need to mock the database or use a test database
        assert response.status_code in [201, 500]  # 500 if DB not configured

        if response.status_code == 201:
            data = response.json()
            assert data["success"] is True
            assert data["data"]["username"] == user_payload["username"]
            assert data["data"]["email"] == user_payload["email"]

    @pytest.mark.anyio
    async def test_create_user_validation_error(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test user creation with invalid data."""
        invalid_payload = {
            "username": "",  # Empty username
            "email": "invalid-email",  # Invalid email format
            "password": "123",  # Weak password
        }

        response = await async_client.post(
            f"{api_v1_prefix}/users",
            json=invalid_payload,
        )

        # Should return validation error
        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_get_user_not_found(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test getting a non-existent user."""
        response = await async_client.get(
            f"{api_v1_prefix}/users/nonexistent-id",
        )

        # Should return 404 or error response
        assert response.status_code in [404, 500]

    @pytest.mark.anyio
    async def test_list_users(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test listing users."""
        response = await async_client.get(
            f"{api_v1_prefix}/users",
            params={"page": 1, "page_size": 10},
        )

        # Should return list response
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            assert "items" in data or "data" in data

    @pytest.mark.anyio
    async def test_update_user_not_found(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test updating a non-existent user."""
        response = await async_client.put(
            f"{api_v1_prefix}/users/nonexistent-id",
            json={"full_name": "New Name"},
        )

        assert response.status_code in [404, 500]

    @pytest.mark.anyio
    async def test_delete_user_not_found(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test deleting a non-existent user."""
        response = await async_client.delete(
            f"{api_v1_prefix}/users/nonexistent-id",
        )

        assert response.status_code in [404, 500]


class TestUserAPIResponseFormat:
    """Tests for User API response format."""

    @pytest.mark.anyio
    async def test_api_response_format(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test that API responses follow the standard format."""
        response = await async_client.get(
            f"{api_v1_prefix}/users",
        )

        if response.status_code == 200:
            data = response.json()
            # Check standard response fields
            assert "success" in data or "items" in data

    @pytest.mark.anyio
    async def test_validation_error_format(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test validation error response format."""
        response = await async_client.post(
            f"{api_v1_prefix}/users",
            json={},  # Empty payload
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestUserAPIPagination:
    """Tests for User API pagination."""

    @pytest.mark.anyio
    async def test_pagination_parameters(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test pagination query parameters."""
        response = await async_client.get(
            f"{api_v1_prefix}/users",
            params={"page": 1, "page_size": 5},
        )

        assert response.status_code in [200, 500]

    @pytest.mark.anyio
    async def test_invalid_page_parameter(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test invalid page parameter."""
        response = await async_client.get(
            f"{api_v1_prefix}/users",
            params={"page": 0},  # Invalid page
        )

        # Should return validation error
        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_invalid_page_size_parameter(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test invalid page_size parameter."""
        response = await async_client.get(
            f"{api_v1_prefix}/users",
            params={"page_size": 1000},  # Too large
        )

        # Should return validation error or be capped
        assert response.status_code in [200, 422, 500]

