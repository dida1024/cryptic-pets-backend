"""Unit tests for Pet command handlers."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from application.pets.command_handlers import (
    CreatePetHandler,
    DeletePetHandler,
    TransferPetOwnershipHandler,
    UpdatePetHandler,
)
from application.pets.commands import (
    CreatePetCommand,
    DeletePetCommand,
    TransferPetOwnershipCommand,
    UpdatePetCommand,
)
from domain.pets.entities import Breed, Pet
from domain.pets.exceptions import (
    BreedNotFoundError,
    PetNotFoundError,
)
from domain.pets.value_objects import GenderEnum
from domain.users.entities import User
from domain.users.exceptions import UserNotFoundError


class TestCreatePetHandler:
    """Test cases for CreatePetHandler."""

    @pytest.fixture
    def existing_user(self):
        """Create an existing user for testing."""
        return User(
            id="user-123",
            username="testuser",
            email="test@example.com",
            hashed_password="hashed",
        )

    @pytest.fixture
    def existing_breed(self):
        """Create an existing breed for testing."""
        from domain.common.value_objects import I18nEnum
        return Breed(
            id="breed-123",
            name={I18nEnum.EN_US: "Corn Snake", I18nEnum.ZH_CN: "玉米蛇"},
        )

    @pytest.fixture
    def mock_repositories(self, existing_user, existing_breed):
        """Create mock repositories."""
        pet_repo = MagicMock()
        pet_repo.create = AsyncMock(side_effect=lambda pet: pet)

        user_repo = MagicMock()
        user_repo.get_by_id = AsyncMock(return_value=existing_user)

        breed_repo = MagicMock()
        breed_repo.get_by_id = AsyncMock(return_value=existing_breed)

        return {
            "pet": pet_repo,
            "user": user_repo,
            "breed": breed_repo,
        }

    @pytest.fixture
    def handler_without_domain_service(self, mock_repositories):
        """Create handler without domain service."""
        return CreatePetHandler(
            pet_repository=mock_repositories["pet"],
            user_repository=mock_repositories["user"],
            breed_repository=mock_repositories["breed"],
            pet_domain_service=None,
        )

    @pytest.mark.anyio
    async def test_create_pet_success(
        self, handler_without_domain_service, mock_repositories
    ):
        """Test successful pet creation."""
        command = CreatePetCommand(
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
            description="A lovely snake",
            gender=GenderEnum.MALE,
        )

        result = await handler_without_domain_service.handle(command)

        assert result.name == "Fluffy"
        assert result.owner_id == "user-123"
        assert result.breed_id == "breed-123"
        assert result.description == "A lovely snake"
        assert result.gender == GenderEnum.MALE
        assert result.id is not None

        mock_repositories["pet"].create.assert_called_once()

    @pytest.mark.anyio
    async def test_create_pet_user_not_found(
        self, handler_without_domain_service, mock_repositories
    ):
        """Test creation fails when user not found."""
        mock_repositories["user"].get_by_id.return_value = None

        command = CreatePetCommand(
            name="Fluffy",
            owner_id="nonexistent",
            breed_id="breed-123",
        )

        with pytest.raises(UserNotFoundError):
            await handler_without_domain_service.handle(command)

    @pytest.mark.anyio
    async def test_create_pet_breed_not_found(
        self, handler_without_domain_service, mock_repositories
    ):
        """Test creation fails when breed not found."""
        mock_repositories["breed"].get_by_id.return_value = None

        command = CreatePetCommand(
            name="Fluffy",
            owner_id="user-123",
            breed_id="nonexistent",
        )

        with pytest.raises(BreedNotFoundError):
            await handler_without_domain_service.handle(command)

    @pytest.mark.anyio
    async def test_create_pet_adds_domain_event(
        self, handler_without_domain_service, mock_repositories
    ):
        """Test that pet creation adds domain event."""

        def capture_pet(pet):
            events = pet.get_domain_events()
            assert len(events) == 1
            assert events[0].pet_id == pet.id
            assert events[0].owner_id == pet.owner_id
            return pet

        mock_repositories["pet"].create.side_effect = capture_pet

        command = CreatePetCommand(
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
        )

        await handler_without_domain_service.handle(command)


class TestTransferPetOwnershipHandler:
    """Test cases for TransferPetOwnershipHandler."""

    @pytest.fixture
    def existing_pet(self):
        """Create an existing pet for testing."""
        return Pet(
            id="pet-123",
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
        )

    @pytest.fixture
    def new_owner(self):
        """Create a new owner for testing."""
        return User(
            id="user-456",
            username="newowner",
            email="new@example.com",
            hashed_password="hashed",
        )

    @pytest.fixture
    def mock_repositories(self, existing_pet, new_owner):
        """Create mock repositories."""
        pet_repo = MagicMock()
        pet_repo.get_by_id = AsyncMock(return_value=existing_pet)
        pet_repo.update = AsyncMock(side_effect=lambda pet: pet)

        user_repo = MagicMock()
        user_repo.get_by_id = AsyncMock(return_value=new_owner)

        return {
            "pet": pet_repo,
            "user": user_repo,
        }

    @pytest.fixture
    def handler_without_domain_service(self, mock_repositories):
        """Create handler without domain service."""
        return TransferPetOwnershipHandler(
            pet_repository=mock_repositories["pet"],
            user_repository=mock_repositories["user"],
            pet_domain_service=None,
        )

    @pytest.mark.anyio
    async def test_transfer_ownership_success(
        self, handler_without_domain_service, mock_repositories
    ):
        """Test successful ownership transfer."""
        command = TransferPetOwnershipCommand(
            pet_id="pet-123",
            new_owner_id="user-456",
            current_user_id="user-123",
        )

        result = await handler_without_domain_service.handle(command)

        assert result.owner_id == "user-456"
        mock_repositories["pet"].update.assert_called_once()

    @pytest.mark.anyio
    async def test_transfer_ownership_pet_not_found(
        self, handler_without_domain_service, mock_repositories
    ):
        """Test transfer fails when pet not found."""
        mock_repositories["pet"].get_by_id.return_value = None

        command = TransferPetOwnershipCommand(
            pet_id="nonexistent",
            new_owner_id="user-456",
            current_user_id="user-123",
        )

        with pytest.raises(PetNotFoundError):
            await handler_without_domain_service.handle(command)

    @pytest.mark.anyio
    async def test_transfer_ownership_not_owner(
        self, handler_without_domain_service, mock_repositories
    ):
        """Test transfer fails when current user is not owner."""
        from domain.pets.exceptions import UnauthorizedPetAccessError

        command = TransferPetOwnershipCommand(
            pet_id="pet-123",
            new_owner_id="user-456",
            current_user_id="user-999",  # Not the owner
        )

        with pytest.raises(UnauthorizedPetAccessError):
            await handler_without_domain_service.handle(command)

    @pytest.mark.anyio
    async def test_transfer_ownership_new_owner_not_found(
        self, handler_without_domain_service, mock_repositories
    ):
        """Test transfer fails when new owner not found."""
        mock_repositories["user"].get_by_id.return_value = None

        command = TransferPetOwnershipCommand(
            pet_id="pet-123",
            new_owner_id="nonexistent",
            current_user_id="user-123",
        )

        with pytest.raises(UserNotFoundError):
            await handler_without_domain_service.handle(command)

    @pytest.mark.anyio
    async def test_transfer_ownership_same_owner(
        self, handler_without_domain_service, mock_repositories
    ):
        """Test transfer fails when transferring to same owner."""
        from domain.pets.exceptions import InvalidOwnershipTransferError

        command = TransferPetOwnershipCommand(
            pet_id="pet-123",
            new_owner_id="user-123",  # Same as current
            current_user_id="user-123",
        )

        with pytest.raises(InvalidOwnershipTransferError):
            await handler_without_domain_service.handle(command)


class TestUpdatePetHandler:
    """Test cases for UpdatePetHandler."""

    @pytest.fixture
    def existing_pet(self):
        """Create an existing pet for testing."""
        return Pet(
            id="pet-123",
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
            gender=GenderEnum.UNKNOWN,
        )

    @pytest.fixture
    def existing_breed(self):
        """Create an existing breed for testing."""
        from domain.common.value_objects import I18nEnum
        return Breed(
            id="breed-456",
            name={I18nEnum.EN_US: "Ball Python"},
        )

    @pytest.fixture
    def mock_repositories(self, existing_pet, existing_breed):
        """Create mock repositories."""
        pet_repo = MagicMock()
        pet_repo.get_by_id = AsyncMock(return_value=existing_pet)
        pet_repo.update = AsyncMock(side_effect=lambda pet: pet)

        breed_repo = MagicMock()
        breed_repo.get_by_id = AsyncMock(return_value=existing_breed)

        return {
            "pet": pet_repo,
            "breed": breed_repo,
        }

    @pytest.fixture
    def handler(self, mock_repositories):
        """Create handler."""
        return UpdatePetHandler(
            pet_repository=mock_repositories["pet"],
            breed_repository=mock_repositories["breed"],
            pet_domain_service=None,
        )

    @pytest.mark.anyio
    async def test_update_pet_name(self, handler, mock_repositories):
        """Test updating pet name."""
        command = UpdatePetCommand(
            pet_id="pet-123",
            name="NewName",
        )

        result = await handler.handle(command)

        assert result.name == "NewName"

    @pytest.mark.anyio
    async def test_update_pet_gender(self, handler, mock_repositories):
        """Test updating pet gender."""
        command = UpdatePetCommand(
            pet_id="pet-123",
            gender=GenderEnum.FEMALE,
        )

        result = await handler.handle(command)

        assert result.gender == GenderEnum.FEMALE

    @pytest.mark.anyio
    async def test_update_pet_breed(self, handler, mock_repositories):
        """Test updating pet breed."""
        command = UpdatePetCommand(
            pet_id="pet-123",
            breed_id="breed-456",
        )

        result = await handler.handle(command)

        assert result.breed_id == "breed-456"

    @pytest.mark.anyio
    async def test_update_pet_not_found(self, handler, mock_repositories):
        """Test update fails when pet not found."""
        mock_repositories["pet"].get_by_id.return_value = None

        command = UpdatePetCommand(
            pet_id="nonexistent",
            name="NewName",
        )

        with pytest.raises(PetNotFoundError):
            await handler.handle(command)

    @pytest.mark.anyio
    async def test_update_pet_breed_not_found(self, handler, mock_repositories):
        """Test update fails when new breed not found."""
        mock_repositories["breed"].get_by_id.return_value = None

        command = UpdatePetCommand(
            pet_id="pet-123",
            breed_id="nonexistent",
        )

        with pytest.raises(BreedNotFoundError):
            await handler.handle(command)


class TestDeletePetHandler:
    """Test cases for DeletePetHandler."""

    @pytest.fixture
    def existing_pet(self):
        """Create an existing pet for testing."""
        return Pet(
            id="pet-123",
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
        )

    @pytest.fixture
    def mock_repository(self, existing_pet):
        """Create mock repository."""
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=existing_pet)
        repo.delete = AsyncMock(return_value=True)
        return repo

    @pytest.fixture
    def handler(self, mock_repository):
        """Create handler."""
        return DeletePetHandler(pet_repository=mock_repository)

    @pytest.mark.anyio
    async def test_delete_pet_success(self, handler, mock_repository):
        """Test successful pet deletion."""
        command = DeletePetCommand(pet_id="pet-123")

        result = await handler.handle(command)

        assert result is True
        mock_repository.delete.assert_called_once()

    @pytest.mark.anyio
    async def test_delete_pet_not_found(self, handler, mock_repository):
        """Test deletion fails when pet not found."""
        mock_repository.get_by_id.return_value = None

        command = DeletePetCommand(pet_id="nonexistent")

        with pytest.raises(PetNotFoundError):
            await handler.handle(command)

    @pytest.mark.anyio
    async def test_delete_pet_adds_domain_event(self, handler, mock_repository):
        """Test that deletion adds domain event."""

        def capture_pet(pet):
            events = pet.get_domain_events()
            assert len(events) == 1
            assert events[0].pet_id == pet.id
            return True

        mock_repository.delete.side_effect = capture_pet

        command = DeletePetCommand(pet_id="pet-123")

        await handler.handle(command)

