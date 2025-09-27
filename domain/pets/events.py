"""Domain events for the pets domain."""

from pydantic import Field

from domain.common.entities import I18n
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


class BreedCreatedEvent(DomainEvent):
    """Event raised when a new breed is created."""

    breed_id: str = Field(..., description="ID of the created breed")
    name: I18n = Field(..., description="Name of the created breed")


class BreedUpdatedEvent(DomainEvent):
    """Event raised when a breed is updated."""

    breed_id: str = Field(..., description="ID of the updated breed")
    name: I18n = Field(..., description="Name of the updated breed")


class BreedDeletedEvent(DomainEvent):
    """Event raised when a breed is deleted."""

    breed_id: str = Field(..., description="ID of the deleted breed")
    name: I18n = Field(..., description="Name of the deleted breed")
