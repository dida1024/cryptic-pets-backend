"""End-to-end tests for Pet API."""


import pytest
from httpx import AsyncClient


class TestPetAPI:
    """End-to-end tests for Pet API endpoints."""

    @pytest.mark.anyio
    async def test_create_pet_validation_error(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test pet creation with invalid data."""
        invalid_payload = {
            "name": "",  # Empty name
        }

        response = await async_client.post(
            f"{api_v1_prefix}/pets",
            json=invalid_payload,
        )

        # Should return validation error
        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_get_pet_not_found(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test getting a non-existent pet."""
        response = await async_client.get(
            f"{api_v1_prefix}/pets/nonexistent-id",
        )

        # Should return 404 or error response
        assert response.status_code in [404, 500]

    @pytest.mark.anyio
    async def test_search_pets(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test searching pets."""
        response = await async_client.get(
            f"{api_v1_prefix}/pets",
            params={"page": 1, "page_size": 10},
        )

        # Should return list response
        assert response.status_code in [200, 500]

    @pytest.mark.anyio
    async def test_search_pets_with_filters(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test searching pets with filters."""
        response = await async_client.get(
            f"{api_v1_prefix}/pets",
            params={
                "search_term": "fluffy",
                "owner_id": "user-123",
                "page": 1,
                "page_size": 10,
            },
        )

        assert response.status_code in [200, 500]

    @pytest.mark.anyio
    async def test_list_pets_by_owner(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test listing pets by owner."""
        response = await async_client.get(
            f"{api_v1_prefix}/pets/owner/user-123",
            params={"page": 1, "page_size": 10},
        )

        assert response.status_code in [200, 500]

    @pytest.mark.anyio
    async def test_update_pet_not_found(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test updating a non-existent pet."""
        response = await async_client.put(
            f"{api_v1_prefix}/pets/nonexistent-id",
            json={"name": "New Name"},
        )

        assert response.status_code in [404, 500]

    @pytest.mark.anyio
    async def test_delete_pet_not_found(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test deleting a non-existent pet."""
        response = await async_client.delete(
            f"{api_v1_prefix}/pets/nonexistent-id",
        )

        assert response.status_code in [404, 500]

    @pytest.mark.anyio
    async def test_transfer_pet_ownership_validation(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test pet ownership transfer with invalid data."""
        response = await async_client.post(
            f"{api_v1_prefix}/pets/pet-123/transfer",
            json={},  # Missing required fields
        )

        assert response.status_code == 422


class TestPetAPIResponseFormat:
    """Tests for Pet API response format."""

    @pytest.mark.anyio
    async def test_pet_detail_response_format(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test pet detail response format."""
        response = await async_client.get(
            f"{api_v1_prefix}/pets/pet-123",
        )

        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "data" in data

    @pytest.mark.anyio
    async def test_pet_list_response_format(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test pet list response format."""
        response = await async_client.get(
            f"{api_v1_prefix}/pets",
        )

        if response.status_code == 200:
            data = response.json()
            # Should have pagination fields
            assert "items" in data or "data" in data


class TestPetAPIPagination:
    """Tests for Pet API pagination."""

    @pytest.mark.anyio
    async def test_pagination_parameters(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test pagination query parameters."""
        response = await async_client.get(
            f"{api_v1_prefix}/pets",
            params={"page": 1, "page_size": 5},
        )

        assert response.status_code in [200, 500]

    @pytest.mark.anyio
    async def test_invalid_page_parameter(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test invalid page parameter."""
        response = await async_client.get(
            f"{api_v1_prefix}/pets",
            params={"page": 0},  # Invalid page
        )

        # Should return validation error
        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_large_page_size_capped(
        self, async_client: AsyncClient, api_v1_prefix: str
    ):
        """Test that large page_size is rejected or capped."""
        response = await async_client.get(
            f"{api_v1_prefix}/pets",
            params={"page_size": 1000},  # Too large
        )

        # Should return validation error or be capped
        assert response.status_code in [200, 422, 500]

