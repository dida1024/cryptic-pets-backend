"""Unit tests for PetDomainService."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from domain.pets.entities import Pet
from domain.pets.exceptions import (
    BreedNotFoundError,
    IncompatibleMorphologyError,
    InvalidOwnershipTransferError,
    MorphologyNotFoundError,
    OwnerNotFoundError,
    PetNotFoundError,
    UnauthorizedPetAccessError,
)
from domain.pets.services import CreatePetData, PetDomainService
from domain.pets.value_objects import GenderEnum


class TestPetDomainServiceCreatePet:
    """Test cases for PetDomainService.create_pet_with_validation."""

    @pytest.fixture
    def mock_repositories(self):
        """Create mock repositories for testing."""
        pet_repo = MagicMock()
        pet_repo.get_by_id = AsyncMock(return_value=None)
        pet_repo.create = AsyncMock()

        user_repo = MagicMock()
        user_repo.get_by_id = AsyncMock(return_value=True)  # User exists

        breed_repo = MagicMock()
        breed_repo.get_by_id = AsyncMock(return_value=True)  # Breed exists

        morphology_repo = MagicMock()
        morphology_repo.get_by_id = AsyncMock(return_value=True)  # Morphology exists
        morphology_repo.is_compatible_with_breed = AsyncMock(return_value=True)

        return {
            "pet": pet_repo,
            "user": user_repo,
            "breed": breed_repo,
            "morphology": morphology_repo,
        }

    @pytest.fixture
    def service(self, mock_repositories):
        """Create a PetDomainService instance with mock repositories."""
        return PetDomainService(
            pet_repository=mock_repositories["pet"],
            user_repository=mock_repositories["user"],
            breed_repository=mock_repositories["breed"],
            morphology_repository=mock_repositories["morphology"],
        )

    @pytest.mark.anyio
    async def test_create_pet_success(self, service, mock_repositories):
        """Test successful pet creation."""
        pet_data = CreatePetData(
            name="Fluffy",
            breed_id="breed-123",
            description="A lovely snake",
            gender=GenderEnum.MALE,
        )

        # Setup mock to return the created pet
        def capture_pet(pet):
            return pet

        mock_repositories["pet"].create.side_effect = capture_pet

        result = await service.create_pet_with_validation(
            pet_data=pet_data,
            owner_id="user-123",
        )

        assert result.name == "Fluffy"
        assert result.owner_id == "user-123"
        assert result.breed_id == "breed-123"
        assert result.gender == GenderEnum.MALE
        assert result.id is not None

        # Verify domain event was added
        events = result.get_domain_events()
        assert len(events) == 1
        assert events[0].pet_id == result.id

    @pytest.mark.anyio
    async def test_create_pet_with_morphology_success(self, service, mock_repositories):
        """Test successful pet creation with morphology."""
        pet_data = CreatePetData(
            name="Fluffy",
            breed_id="breed-123",
            morphology_id="morph-123",
        )

        def capture_pet(pet):
            return pet

        mock_repositories["pet"].create.side_effect = capture_pet

        result = await service.create_pet_with_validation(
            pet_data=pet_data,
            owner_id="user-123",
        )

        assert result.morphology_id == "morph-123"

        # Verify morphology compatibility was checked
        mock_repositories["morphology"].is_compatible_with_breed.assert_called_once_with(
            "morph-123", "breed-123"
        )

    @pytest.mark.anyio
    async def test_create_pet_owner_not_found(self, service, mock_repositories):
        """Test pet creation fails when owner not found."""
        mock_repositories["user"].get_by_id.return_value = None

        pet_data = CreatePetData(
            name="Fluffy",
            breed_id="breed-123",
        )

        with pytest.raises(OwnerNotFoundError):
            await service.create_pet_with_validation(
                pet_data=pet_data,
                owner_id="nonexistent-user",
            )

    @pytest.mark.anyio
    async def test_create_pet_breed_not_found(self, service, mock_repositories):
        """Test pet creation fails when breed not found."""
        mock_repositories["breed"].get_by_id.return_value = None

        pet_data = CreatePetData(
            name="Fluffy",
            breed_id="nonexistent-breed",
        )

        with pytest.raises(BreedNotFoundError):
            await service.create_pet_with_validation(
                pet_data=pet_data,
                owner_id="user-123",
            )

    @pytest.mark.anyio
    async def test_create_pet_morphology_not_found(self, service, mock_repositories):
        """Test pet creation fails when morphology not found."""
        mock_repositories["morphology"].get_by_id.return_value = None

        pet_data = CreatePetData(
            name="Fluffy",
            breed_id="breed-123",
            morphology_id="nonexistent-morph",
        )

        with pytest.raises(MorphologyNotFoundError):
            await service.create_pet_with_validation(
                pet_data=pet_data,
                owner_id="user-123",
            )

    @pytest.mark.anyio
    async def test_create_pet_incompatible_morphology(self, service, mock_repositories):
        """Test pet creation fails when morphology is incompatible with breed."""
        mock_repositories["morphology"].is_compatible_with_breed.return_value = False

        pet_data = CreatePetData(
            name="Fluffy",
            breed_id="breed-123",
            morphology_id="incompatible-morph",
        )

        with pytest.raises(IncompatibleMorphologyError):
            await service.create_pet_with_validation(
                pet_data=pet_data,
                owner_id="user-123",
            )


class TestPetDomainServiceTransferOwnership:
    """Test cases for PetDomainService.transfer_pet_ownership."""

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
    def mock_repositories(self, existing_pet):
        """Create mock repositories for testing."""
        pet_repo = MagicMock()
        pet_repo.get_by_id = AsyncMock(return_value=existing_pet)
        pet_repo.update = AsyncMock(side_effect=lambda pet: pet)

        user_repo = MagicMock()
        user_repo.get_by_id = AsyncMock(return_value=True)

        breed_repo = MagicMock()
        morphology_repo = MagicMock()

        return {
            "pet": pet_repo,
            "user": user_repo,
            "breed": breed_repo,
            "morphology": morphology_repo,
        }

    @pytest.fixture
    def service(self, mock_repositories):
        """Create a PetDomainService instance with mock repositories."""
        return PetDomainService(
            pet_repository=mock_repositories["pet"],
            user_repository=mock_repositories["user"],
            breed_repository=mock_repositories["breed"],
            morphology_repository=mock_repositories["morphology"],
        )

    @pytest.mark.anyio
    async def test_transfer_ownership_success(self, service, mock_repositories):
        """Test successful ownership transfer."""
        result = await service.transfer_pet_ownership(
            pet_id="pet-123",
            new_owner_id="user-456",
            current_user_id="user-123",  # Current owner
        )

        assert result.owner_id == "user-456"
        mock_repositories["pet"].update.assert_called_once()

    @pytest.mark.anyio
    async def test_transfer_ownership_pet_not_found(self, service, mock_repositories):
        """Test transfer fails when pet not found."""
        mock_repositories["pet"].get_by_id.return_value = None

        with pytest.raises(PetNotFoundError):
            await service.transfer_pet_ownership(
                pet_id="nonexistent-pet",
                new_owner_id="user-456",
                current_user_id="user-123",
            )

    @pytest.mark.anyio
    async def test_transfer_ownership_not_owner(self, service, mock_repositories):
        """Test transfer fails when current user is not the owner."""
        with pytest.raises(UnauthorizedPetAccessError):
            await service.transfer_pet_ownership(
                pet_id="pet-123",
                new_owner_id="user-456",
                current_user_id="user-999",  # Not the owner
            )

    @pytest.mark.anyio
    async def test_transfer_ownership_new_owner_not_found(
        self, service, mock_repositories
    ):
        """Test transfer fails when new owner not found."""
        mock_repositories["user"].get_by_id.return_value = None

        with pytest.raises(OwnerNotFoundError):
            await service.transfer_pet_ownership(
                pet_id="pet-123",
                new_owner_id="nonexistent-user",
                current_user_id="user-123",
            )

    @pytest.mark.anyio
    async def test_transfer_ownership_same_owner(self, service, mock_repositories):
        """Test transfer fails when transferring to the same owner."""
        with pytest.raises(InvalidOwnershipTransferError):
            await service.transfer_pet_ownership(
                pet_id="pet-123",
                new_owner_id="user-123",  # Same as current owner
                current_user_id="user-123",
            )

    @pytest.mark.anyio
    async def test_transfer_ownership_emits_event(self, service, mock_repositories):
        """Test that ownership transfer emits domain event."""
        result = await service.transfer_pet_ownership(
            pet_id="pet-123",
            new_owner_id="user-456",
            current_user_id="user-123",
        )

        events = result.get_domain_events()
        assert len(events) == 1
        assert events[0].pet_id == "pet-123"
        assert events[0].old_owner_id == "user-123"
        assert events[0].new_owner_id == "user-456"


class TestPetDomainServiceUpdateMorphology:
    """Test cases for PetDomainService.update_pet_morphology."""

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
    def mock_repositories(self):
        """Create mock repositories for testing."""
        pet_repo = MagicMock()
        user_repo = MagicMock()
        breed_repo = MagicMock()

        morphology_repo = MagicMock()
        morphology_repo.get_by_id = AsyncMock(return_value=True)
        morphology_repo.is_compatible_with_breed = AsyncMock(return_value=True)

        return {
            "pet": pet_repo,
            "user": user_repo,
            "breed": breed_repo,
            "morphology": morphology_repo,
        }

    @pytest.fixture
    def service(self, mock_repositories):
        """Create a PetDomainService instance with mock repositories."""
        return PetDomainService(
            pet_repository=mock_repositories["pet"],
            user_repository=mock_repositories["user"],
            breed_repository=mock_repositories["breed"],
            morphology_repository=mock_repositories["morphology"],
        )

    @pytest.mark.anyio
    async def test_update_morphology_success(
        self, service, existing_pet, mock_repositories
    ):
        """Test successful morphology update."""
        result = await service.update_pet_morphology(
            pet=existing_pet,
            morphology_id="morph-123",
            current_user_id="user-123",  # Owner
        )

        assert result.morphology_id == "morph-123"

    @pytest.mark.anyio
    async def test_update_morphology_not_owner(self, service, existing_pet):
        """Test morphology update fails when user is not owner."""
        with pytest.raises(UnauthorizedPetAccessError):
            await service.update_pet_morphology(
                pet=existing_pet,
                morphology_id="morph-123",
                current_user_id="user-999",  # Not the owner
            )

    @pytest.mark.anyio
    async def test_update_morphology_not_found(
        self, service, existing_pet, mock_repositories
    ):
        """Test morphology update fails when morphology not found."""
        mock_repositories["morphology"].get_by_id.return_value = None

        with pytest.raises(MorphologyNotFoundError):
            await service.update_pet_morphology(
                pet=existing_pet,
                morphology_id="nonexistent-morph",
                current_user_id="user-123",
            )

    @pytest.mark.anyio
    async def test_update_morphology_incompatible(
        self, service, existing_pet, mock_repositories
    ):
        """Test morphology update fails when incompatible with breed."""
        mock_repositories["morphology"].is_compatible_with_breed.return_value = False

        with pytest.raises(IncompatibleMorphologyError):
            await service.update_pet_morphology(
                pet=existing_pet,
                morphology_id="incompatible-morph",
                current_user_id="user-123",
            )

    @pytest.mark.anyio
    async def test_update_morphology_to_none(self, service, existing_pet):
        """Test clearing morphology by setting to None."""
        existing_pet.morphology_id = "morph-123"

        result = await service.update_pet_morphology(
            pet=existing_pet,
            morphology_id=None,
            current_user_id="user-123",
        )

        assert result.morphology_id is None

    @pytest.mark.anyio
    async def test_update_morphology_emits_event(self, service, existing_pet):
        """Test that morphology update emits domain event."""
        result = await service.update_pet_morphology(
            pet=existing_pet,
            morphology_id="morph-123",
            current_user_id="user-123",
        )

        events = result.get_domain_events()
        assert len(events) == 1
        assert events[0].pet_id == "pet-123"
        assert events[0].morphology_id == "morph-123"


class TestCreatePetData:
    """Test cases for CreatePetData DTO."""

    def test_create_pet_data_with_required_fields(self):
        """Test creating CreatePetData with required fields."""
        data = CreatePetData(
            name="Fluffy",
            breed_id="breed-123",
        )

        assert data.name == "Fluffy"
        assert data.breed_id == "breed-123"
        assert data.description is None
        assert data.birth_date is None
        assert data.gender == GenderEnum.UNKNOWN
        assert data.morphology_id is None
        assert data.extra_gene_list == []

    def test_create_pet_data_with_all_fields(self):
        """Test creating CreatePetData with all fields."""
        birth_date = datetime(2023, 1, 15)
        data = CreatePetData(
            name="Sunny",
            breed_id="breed-123",
            description="A beautiful snake",
            birth_date=birth_date,
            gender=GenderEnum.FEMALE,
            morphology_id="morph-123",
            extra_gene_list=["gene-1", "gene-2"],
        )

        assert data.name == "Sunny"
        assert data.breed_id == "breed-123"
        assert data.description == "A beautiful snake"
        assert data.birth_date == birth_date
        assert data.gender == GenderEnum.FEMALE
        assert data.morphology_id == "morph-123"
        assert data.extra_gene_list == ["gene-1", "gene-2"]

