"""Integration tests for User repository."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from domain.common.event_publisher import EventPublisher
from domain.users.entities import User
from domain.users.value_objects import UserTypeEnum
from infrastructure.persistence.postgres.mappers.user_mapper import UserMapper
from infrastructure.persistence.postgres.repositories.user_repository_impl import (
    PostgreSQLUserRepositoryImpl,
)


class TestUserRepositoryIntegration:
    """Integration tests for PostgreSQLUserRepositoryImpl."""

    @pytest.fixture
    def repository(
        self, db_session: AsyncSession, user_mapper: UserMapper, event_publisher: EventPublisher
    ) -> PostgreSQLUserRepositoryImpl:
        """Create a user repository instance."""
        return PostgreSQLUserRepositoryImpl(db_session, user_mapper, event_publisher)

    @pytest.fixture
    def sample_user(self) -> User:
        """Create a sample user for testing."""
        return User(
            id="user-123",
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashed_password_123",
            user_type=UserTypeEnum.USER,
            is_active=True,
        )

    @pytest.mark.anyio
    async def test_create_user(self, repository, sample_user):
        """Test creating a user."""
        result = await repository.create(sample_user)

        assert result.id == sample_user.id
        assert result.username == sample_user.username
        assert result.email == sample_user.email
        assert result.full_name == sample_user.full_name

    @pytest.mark.anyio
    async def test_get_user_by_id(self, repository, sample_user):
        """Test getting a user by ID."""
        await repository.create(sample_user)

        result = await repository.get_by_id(sample_user.id)

        assert result is not None
        assert result.id == sample_user.id
        assert result.username == sample_user.username

    @pytest.mark.anyio
    async def test_get_user_by_id_not_found(self, repository):
        """Test getting a non-existent user by ID."""
        result = await repository.get_by_id("nonexistent-id")

        assert result is None

    @pytest.mark.anyio
    async def test_get_user_by_username(self, repository, sample_user):
        """Test getting a user by username."""
        await repository.create(sample_user)

        result = await repository.get_by_username(sample_user.username)

        assert result is not None
        assert result.username == sample_user.username

    @pytest.mark.anyio
    async def test_get_user_by_email(self, repository, sample_user):
        """Test getting a user by email."""
        await repository.create(sample_user)

        result = await repository.get_by_email(sample_user.email)

        assert result is not None
        assert result.email == sample_user.email

    @pytest.mark.anyio
    async def test_exists_by_username(self, repository, sample_user):
        """Test checking if username exists."""
        assert await repository.exists_by_username(sample_user.username) is False

        await repository.create(sample_user)

        assert await repository.exists_by_username(sample_user.username) is True
        assert await repository.exists_by_username("nonexistent") is False

    @pytest.mark.anyio
    async def test_exists_by_email(self, repository, sample_user):
        """Test checking if email exists."""
        assert await repository.exists_by_email(sample_user.email) is False

        await repository.create(sample_user)

        assert await repository.exists_by_email(sample_user.email) is True
        assert await repository.exists_by_email("nonexistent@example.com") is False

    @pytest.mark.anyio
    async def test_exists_by_username_exclude_id(self, repository, sample_user):
        """Test checking username exists with exclusion."""
        await repository.create(sample_user)

        # Should not exist when excluding the same user
        assert (
            await repository.exists_by_username(
                sample_user.username, exclude_id=sample_user.id
            )
            is False
        )

        # Should exist when not excluding
        assert await repository.exists_by_username(sample_user.username) is True

    @pytest.mark.anyio
    async def test_update_user(self, repository, sample_user):
        """Test updating a user."""
        created = await repository.create(sample_user)

        created.full_name = "Updated Name"
        created.is_active = False

        result = await repository.update(created)

        assert result.full_name == "Updated Name"
        assert result.is_active is False

    @pytest.mark.anyio
    async def test_delete_user_soft_delete(self, repository, sample_user):
        """Test soft deleting a user."""
        await repository.create(sample_user)

        result = await repository.delete(sample_user.id)

        assert result is True

        # Should not find deleted user
        found = await repository.get_by_id(sample_user.id)
        assert found is None

    @pytest.mark.anyio
    async def test_list_all_users(self, repository):
        """Test listing all users."""
        # Create multiple users
        for i in range(5):
            user = User(
                id=f"user-{i}",
                username=f"user{i}",
                email=f"user{i}@example.com",
                hashed_password="hashed",
            )
            await repository.create(user)

        users, total = await repository.list_all(page=1, page_size=10)

        assert len(users) == 5
        assert total == 5

    @pytest.mark.anyio
    async def test_list_all_users_pagination(self, repository):
        """Test user list pagination."""
        # Create multiple users
        for i in range(10):
            user = User(
                id=f"user-{i}",
                username=f"user{i}",
                email=f"user{i}@example.com",
                hashed_password="hashed",
            )
            await repository.create(user)

        # Get first page
        users_page1, total = await repository.list_all(page=1, page_size=3)
        assert len(users_page1) == 3
        assert total == 10

        # Get second page
        users_page2, _ = await repository.list_all(page=2, page_size=3)
        assert len(users_page2) == 3

        # Ensure no overlap
        page1_ids = {u.id for u in users_page1}
        page2_ids = {u.id for u in users_page2}
        assert len(page1_ids & page2_ids) == 0

    @pytest.mark.anyio
    async def test_list_excludes_deleted(self, repository, sample_user):
        """Test that list excludes soft-deleted users."""
        await repository.create(sample_user)
        await repository.delete(sample_user.id)

        users, total = await repository.list_all()

        assert total == 0
        assert len(users) == 0

    @pytest.mark.anyio
    async def test_list_includes_deleted_when_requested(self, repository, sample_user):
        """Test that list can include soft-deleted users."""
        await repository.create(sample_user)
        await repository.delete(sample_user.id)

        users, total = await repository.list_all(include_deleted=True)

        assert total == 1
        assert len(users) == 1

