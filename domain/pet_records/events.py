"""Domain events for the pet records domain."""

from pydantic import Field

from domain.common.events import DomainEvent
from domain.pet_records.value_objects import PetEventTypeEnum


class PetRecordCreatedEvent(DomainEvent):
    """Event raised when a new pet record is created."""

    record_id: str = Field(...)
    pet_id: str = Field(...)
    event_type: PetEventTypeEnum = Field(...)


class PetRecordUpdatedEvent(DomainEvent):
    """Event raised when a pet record is updated."""

    record_id: str = Field(...)
    pet_id: str = Field(...)
    event_type: PetEventTypeEnum = Field(...)


class PetRecordDeletedEvent(DomainEvent):
    """Event raised when a pet record is deleted."""

    record_id: str = Field(...)
    pet_id: str = Field(...)
    event_type: PetEventTypeEnum = Field(...)
