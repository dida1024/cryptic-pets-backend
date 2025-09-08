"""Domain events for the users domain."""

from pydantic import Field

from domain.common.events import DomainEvent


class PetRecordCreatedEvent(DomainEvent):
    """Event raised when a new user is created."""

    pet_id: str = Field(...)
    record_type: str = Field(...)
    record_data: dict = Field(...)


class PetRecordUpdatedEvent(DomainEvent):
    """Event raised when pet record information is updated."""

    pet_id: str = Field(...)
    record_type: str = Field(...)
    record_data: dict = Field(...)
    updated_fields: list[str] = Field(...)


class PetRecordDeletedEvent(DomainEvent):
    """Event raised when a pet record is deleted."""

    user_id: str = Field(...)
    record_type: str = Field(...)
    record_data: dict = Field(...)


class PetRecordPasswordChangedEvent(DomainEvent):
    """Event raised when user password is changed."""

    pet_id: str = Field(...)
    record_type: str = Field(...)
    record_data: dict = Field(...)
