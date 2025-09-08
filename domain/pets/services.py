"""Domain services for the pets domain."""

from datetime import datetime
from typing import Protocol

from domain.pets.entities import Pet
from domain.pets.events import PetCreatedEvent, PetOwnershipChangedEvent, PetMorphologyUpdatedEvent
from domain.pets.exceptions import (
    BreedNotFoundError,
    IncompatibleMorphologyError,
    InvalidOwnershipTransferError,
    MorphologyNotFoundError,
    OwnerNotFoundError,
    PetNotFoundError,
    UnauthorizedPetAccessError,
)
from domain.pets.value_objects import GenderEnum


class UserRepositoryProtocol(Protocol):
    """Protocol for user repository operations needed by pet domain service."""
    
    async def get_by_id(self, user_id: str) -> bool:
        """Check if a user exists by ID."""
        ...


class BreedRepositoryProtocol(Protocol):
    """Protocol for breed repository operations needed by pet domain service."""
    
    async def get_by_id(self, breed_id: str) -> bool:
        """Check if a breed exists by ID."""
        ...


class MorphologyRepositoryProtocol(Protocol):
    """Protocol for morphology repository operations needed by pet domain service."""
    
    async def get_by_id(self, morphology_id: str) -> bool:
        """Check if a morphology exists by ID."""
        ...
    
    async def is_compatible_with_breed(self, morphology_id: str, breed_id: str) -> bool:
        """Check if a morphology is compatible with a breed."""
        ...


class PetRepositoryProtocol(Protocol):
    """Protocol for pet repository operations needed by pet domain service."""
    
    async def get_by_id(self, pet_id: str) -> Pet | None:
        """Get a pet by ID."""
        ...
    
    async def create(self, pet: Pet) -> Pet:
        """Create a new pet."""
        ...
    
    async def update(self, pet: Pet) -> Pet:
        """Update an existing pet."""
        ...


class CreatePetData:
    """Data transfer object for pet creation."""
    
    def __init__(
        self,
        name: str,
        breed_id: str,
        description: str | None = None,
        birth_date: datetime | None = None,
        gender: GenderEnum = GenderEnum.UNKNOWN,
        morphology_id: str | None = None,
        extra_gene_list: list = None,
    ):
        self.name = name
        self.breed_id = breed_id
        self.description = description
        self.birth_date = birth_date
        self.gender = gender
        self.morphology_id = morphology_id
        self.extra_gene_list = extra_gene_list or []


class PetDomainService:
    """Domain service for complex pet-related business logic across aggregates."""
    
    def __init__(
        self,
        pet_repository: PetRepositoryProtocol,
        user_repository: UserRepositoryProtocol,
        breed_repository: BreedRepositoryProtocol,
        morphology_repository: MorphologyRepositoryProtocol,
    ):
        self.pet_repository = pet_repository
        self.user_repository = user_repository
        self.breed_repository = breed_repository
        self.morphology_repository = morphology_repository
    
    async def create_pet_with_validation(
        self,
        pet_data: CreatePetData,
        owner_id: str,
    ) -> Pet:
        """Create a pet with full validation across aggregates."""
        
        # Validate owner exists
        owner_exists = await self.user_repository.get_by_id(owner_id)
        if not owner_exists:
            raise OwnerNotFoundError(f"Owner with ID {owner_id} not found")
        
        # Validate breed exists
        breed_exists = await self.breed_repository.get_by_id(pet_data.breed_id)
        if not breed_exists:
            raise BreedNotFoundError(f"Breed with ID {pet_data.breed_id} not found")
        
        # Validate morphology if provided
        if pet_data.morphology_id:
            morphology_exists = await self.morphology_repository.get_by_id(pet_data.morphology_id)
            if not morphology_exists:
                raise MorphologyNotFoundError(f"Morphology with ID {pet_data.morphology_id} not found")
            
            # Validate morphology is compatible with breed
            is_compatible = await self.morphology_repository.is_compatible_with_breed(
                pet_data.morphology_id, 
                pet_data.breed_id
            )
            if not is_compatible:
                raise IncompatibleMorphologyError(
                    f"Morphology {pet_data.morphology_id} is not compatible with breed {pet_data.breed_id}"
                )
        
        # Create pet entity
        pet = Pet(
            name=pet_data.name,
            description=pet_data.description,
            birth_date=pet_data.birth_date,
            owner_id=owner_id,
            breed_id=pet_data.breed_id,
            gender=pet_data.gender,
            morphology_id=pet_data.morphology_id,
            extra_gene_list=pet_data.extra_gene_list,
        )
        
        # Add domain event
        created_pet = await self.pet_repository.create(pet)
        created_pet._add_domain_event(
            PetCreatedEvent(
                pet_id=created_pet.id,
                owner_id=created_pet.owner_id,
                breed_id=created_pet.breed_id,
            )
        )
        
        return created_pet
    
    async def transfer_pet_ownership(
        self,
        pet_id: str,
        new_owner_id: str,
        current_user_id: str,
    ) -> Pet:
        """Transfer pet ownership with business rules validation."""
        
        # Get pet
        pet = await self.pet_repository.get_by_id(pet_id)
        if not pet:
            raise PetNotFoundError(f"Pet with ID {pet_id} not found")
        
        # Validate current user is the owner
        if pet.owner_id != current_user_id:
            raise UnauthorizedPetAccessError("Only the current owner can transfer ownership")
        
        # Validate new owner exists
        new_owner_exists = await self.user_repository.get_by_id(new_owner_id)
        if not new_owner_exists:
            raise OwnerNotFoundError(f"New owner with ID {new_owner_id} not found")
        
        # Business rule: Cannot transfer to the same owner
        if pet.owner_id == new_owner_id:
            raise InvalidOwnershipTransferError("Cannot transfer pet to the same owner")
        
        # Execute the transfer using the domain entity method
        pet.change_owner(new_owner_id)
        
        # Save and return
        return await self.pet_repository.update(pet)
    
    async def update_pet_morphology(
        self,
        pet_id: str,
        morphology_id: str | None,
        current_user_id: str,
    ) -> Pet:
        """Update pet morphology with validation."""
        
        # Get pet
        pet = await self.pet_repository.get_by_id(pet_id)
        if not pet:
            raise PetNotFoundError(f"Pet with ID {pet_id} not found")
        
        # Validate current user is the owner
        if pet.owner_id != current_user_id:
            raise UnauthorizedPetAccessError("Only the owner can update pet morphology")
        
        # Validate morphology if provided
        if morphology_id:
            morphology_exists = await self.morphology_repository.get_by_id(morphology_id)
            if not morphology_exists:
                raise MorphologyNotFoundError(f"Morphology with ID {morphology_id} not found")
            
            # Validate morphology is compatible with breed
            is_compatible = await self.morphology_repository.is_compatible_with_breed(
                morphology_id, 
                pet.breed_id
            )
            if not is_compatible:
                raise IncompatibleMorphologyError(
                    f"Morphology {morphology_id} is not compatible with breed {pet.breed_id}"
                )
        
        # Execute the update using the domain entity method
        pet.update_morphology(morphology_id)
        
        # Save and return
        return await self.pet_repository.update(pet)
