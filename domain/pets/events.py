"""Domain events for the pets domain."""

from pydantic import Field

from domain.common.events import DomainEvent


class PetCreatedEvent(DomainEvent):
    """Event raised when a new pet is created."""
    
    pet_id: str = Field(...)
    owner_id: str = Field(...)
    breed_id: str = Field(...)


class PetOwnershipChangedEvent(DomainEvent):
    """Event raised when pet ownership changes."""
    
    pet_id: str = Field(...)
    old_owner_id: str = Field(...)
    new_owner_id: str = Field(...)


class PetMorphologyUpdatedEvent(DomainEvent):
    """Event raised when pet morphology is updated."""
    
    pet_id: str = Field(...)
    morphology_id: str | None = Field(...)


class PetDeletedEvent(DomainEvent):
    """Event raised when a pet is deleted."""
    
    pet_id: str = Field(...)
    owner_id: str = Field(...)