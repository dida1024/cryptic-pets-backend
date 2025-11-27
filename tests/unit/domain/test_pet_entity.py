"""Unit tests for Pet entity."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from domain.pets.entities import Pet
from domain.pets.events import (
    PetMorphologyUpdatedEvent,
    PetOwnershipChangedEvent,
)
from domain.pets.value_objects import GenderEnum


class TestPetEntity:
    """Test cases for Pet entity."""

    def test_create_pet_with_required_fields(self):
        """Test creating a pet with only required fields."""
        pet = Pet(
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
        )

        assert pet.name == "Fluffy"
        assert pet.owner_id == "user-123"
        assert pet.breed_id == "breed-123"
        assert pet.description is None  # optional
        assert pet.birth_date is None  # optional
        assert pet.gender == GenderEnum.UNKNOWN  # default
        assert pet.morphology_id is None  # optional
        assert pet.extra_gene_list == []  # default
        assert pet.picture_list == []  # default

    def test_create_pet_with_all_fields(self):
        """Test creating a pet with all fields."""
        birth_date = datetime(2023, 1, 15)
        pet = Pet(
            id="pet-123",
            name="Sunny",
            description="A beautiful corn snake",
            birth_date=birth_date,
            owner_id="user-456",
            breed_id="breed-789",
            gender=GenderEnum.FEMALE,
            morphology_id="morph-123",
        )

        assert pet.id == "pet-123"
        assert pet.name == "Sunny"
        assert pet.description == "A beautiful corn snake"
        assert pet.birth_date == birth_date
        assert pet.owner_id == "user-456"
        assert pet.breed_id == "breed-789"
        assert pet.gender == GenderEnum.FEMALE
        assert pet.morphology_id == "morph-123"

    def test_pet_inherits_base_entity_fields(self):
        """Test that pet has BaseEntity fields."""
        pet = Pet(
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
        )

        assert pet.created_at is not None
        assert pet.updated_at is not None
        assert pet.is_deleted is False
        assert isinstance(pet.created_at, datetime)
        assert isinstance(pet.updated_at, datetime)

    def test_pet_mark_as_deleted(self):
        """Test soft delete functionality."""
        pet = Pet(
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
        )
        original_updated_at = pet.updated_at

        pet.mark_as_deleted()

        assert pet.is_deleted is True
        assert pet.updated_at >= original_updated_at

    def test_pet_equality_by_id(self):
        """Test that pets are equal if their IDs are equal."""
        pet1 = Pet(
            id="pet-123",
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
        )
        pet2 = Pet(
            id="pet-123",
            name="Sunny",  # different name
            owner_id="user-456",  # different owner
            breed_id="breed-456",  # different breed
        )

        assert pet1 == pet2

    def test_pet_inequality_by_id(self):
        """Test that pets are not equal if their IDs differ."""
        pet1 = Pet(
            id="pet-123",
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
        )
        pet2 = Pet(
            id="pet-456",
            name="Fluffy",  # same name
            owner_id="user-123",  # same owner
            breed_id="breed-123",  # same breed
        )

        assert pet1 != pet2

    def test_pet_genders(self):
        """Test different pet genders."""
        male = Pet(
            name="Male",
            owner_id="user-123",
            breed_id="breed-123",
            gender=GenderEnum.MALE,
        )
        female = Pet(
            name="Female",
            owner_id="user-123",
            breed_id="breed-123",
            gender=GenderEnum.FEMALE,
        )
        unknown = Pet(
            name="Unknown",
            owner_id="user-123",
            breed_id="breed-123",
            gender=GenderEnum.UNKNOWN,
        )

        assert male.gender == GenderEnum.MALE
        assert female.gender == GenderEnum.FEMALE
        assert unknown.gender == GenderEnum.UNKNOWN


class TestPetChangeOwner:
    """Test cases for Pet.change_owner method."""

    def test_change_owner_updates_owner_id(self):
        """Test that change_owner updates the owner_id."""
        pet = Pet(
            id="pet-123",
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
        )

        pet.change_owner("user-456")

        assert pet.owner_id == "user-456"

    def test_change_owner_updates_timestamp(self):
        """Test that change_owner updates the timestamp."""
        pet = Pet(
            id="pet-123",
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
        )
        original_updated_at = pet.updated_at

        pet.change_owner("user-456")

        assert pet.updated_at >= original_updated_at

    def test_change_owner_raises_domain_event(self):
        """Test that change_owner emits PetOwnershipChangedEvent."""
        pet = Pet(
            id="pet-123",
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
        )

        pet.change_owner("user-456")

        events = pet.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], PetOwnershipChangedEvent)
        assert events[0].pet_id == "pet-123"
        assert events[0].old_owner_id == "user-123"
        assert events[0].new_owner_id == "user-456"

    def test_change_owner_raises_error_for_empty_owner_id(self):
        """Test that change_owner raises error for empty owner_id."""
        pet = Pet(
            id="pet-123",
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
        )

        with pytest.raises(ValueError, match="Owner ID cannot be empty"):
            pet.change_owner("")

    def test_change_owner_raises_error_for_none_owner_id(self):
        """Test that change_owner raises error for None owner_id."""
        pet = Pet(
            id="pet-123",
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
        )

        with pytest.raises(ValueError, match="Owner ID cannot be empty"):
            pet.change_owner(None)

    def test_change_owner_multiple_times(self):
        """Test changing owner multiple times."""
        pet = Pet(
            id="pet-123",
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
        )

        pet.change_owner("user-456")
        pet.change_owner("user-789")

        assert pet.owner_id == "user-789"

        events = pet.get_domain_events()
        assert len(events) == 2
        assert events[0].new_owner_id == "user-456"
        assert events[1].old_owner_id == "user-456"
        assert events[1].new_owner_id == "user-789"


class TestPetUpdateMorphology:
    """Test cases for Pet.update_morphology method."""

    def test_update_morphology_sets_morphology_id(self):
        """Test that update_morphology sets the morphology_id."""
        pet = Pet(
            id="pet-123",
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
        )

        pet.update_morphology("morph-123")

        assert pet.morphology_id == "morph-123"

    def test_update_morphology_updates_timestamp(self):
        """Test that update_morphology updates the timestamp."""
        pet = Pet(
            id="pet-123",
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
        )
        original_updated_at = pet.updated_at

        pet.update_morphology("morph-123")

        assert pet.updated_at >= original_updated_at

    def test_update_morphology_raises_domain_event(self):
        """Test that update_morphology emits PetMorphologyUpdatedEvent."""
        pet = Pet(
            id="pet-123",
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
        )

        pet.update_morphology("morph-123")

        events = pet.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], PetMorphologyUpdatedEvent)
        assert events[0].pet_id == "pet-123"
        assert events[0].morphology_id == "morph-123"

    def test_update_morphology_to_none(self):
        """Test clearing morphology by setting to None."""
        pet = Pet(
            id="pet-123",
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
            morphology_id="morph-123",
        )

        pet.update_morphology(None)

        assert pet.morphology_id is None

        events = pet.get_domain_events()
        assert len(events) == 1
        assert events[0].morphology_id is None

    def test_update_morphology_multiple_times(self):
        """Test updating morphology multiple times."""
        pet = Pet(
            id="pet-123",
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
        )

        pet.update_morphology("morph-123")
        pet.update_morphology("morph-456")

        assert pet.morphology_id == "morph-456"

        events = pet.get_domain_events()
        assert len(events) == 2


class TestPetDomainEvents:
    """Test cases for Pet domain events infrastructure."""

    def test_pet_has_domain_events_list(self):
        """Test that pet has domain events infrastructure."""
        pet = Pet(
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
        )

        events = pet.get_domain_events()
        assert events == []

    def test_pet_can_clear_domain_events(self):
        """Test that pet can clear domain events."""
        pet = Pet(
            id="pet-123",
            name="Fluffy",
            owner_id="user-123",
            breed_id="breed-123",
        )

        pet.change_owner("user-456")
        assert len(pet.get_domain_events()) == 1

        pet.clear_domain_events()
        assert pet.get_domain_events() == []


class TestPetModelSerialization:
    """Test cases for Pet model serialization."""

    def test_pet_model_dump(self):
        """Test that pet can be serialized to dict."""
        birth_date = datetime(2023, 1, 15)
        pet = Pet(
            id="pet-123",
            name="Fluffy",
            description="A lovely pet",
            birth_date=birth_date,
            owner_id="user-123",
            breed_id="breed-123",
            gender=GenderEnum.MALE,
            morphology_id="morph-123",
        )

        data = pet.model_dump()

        assert data["id"] == "pet-123"
        assert data["name"] == "Fluffy"
        assert data["description"] == "A lovely pet"
        assert data["birth_date"] == birth_date
        assert data["owner_id"] == "user-123"
        assert data["breed_id"] == "breed-123"
        assert data["gender"] == GenderEnum.MALE
        assert data["morphology_id"] == "morph-123"

    def test_pet_from_attributes(self):
        """Test creating pet from ORM model attributes."""

        class MockORMPet:
            id = "pet-123"
            name = "Fluffy"
            description = "A pet"
            birth_date = None
            owner_id = "user-123"
            breed_id = "breed-123"
            gender = GenderEnum.MALE
            morphology_id = None
            extra_gene_list = []
            picture_list = []
            is_deleted = False
            created_at = datetime.now()
            updated_at = datetime.now()

        pet = Pet.model_validate(MockORMPet())

        assert pet.id == "pet-123"
        assert pet.name == "Fluffy"
        assert pet.owner_id == "user-123"


class TestPetValidation:
    """Test cases for Pet field validation."""

    def test_pet_requires_name(self):
        """Test that name is required."""
        with pytest.raises(ValidationError):
            Pet(
                owner_id="user-123",
                breed_id="breed-123",
            )

    def test_pet_requires_owner_id(self):
        """Test that owner_id is required."""
        with pytest.raises(ValidationError):
            Pet(
                name="Fluffy",
                breed_id="breed-123",
            )

    def test_pet_requires_breed_id(self):
        """Test that breed_id is required."""
        with pytest.raises(ValidationError):
            Pet(
                name="Fluffy",
                owner_id="user-123",
            )

    def test_pet_forbids_extra_fields(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError):
            Pet(
                name="Fluffy",
                owner_id="user-123",
                breed_id="breed-123",
                extra_field="not_allowed",
            )

