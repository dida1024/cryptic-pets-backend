"""Domain events for the users domain."""

from pydantic import Field

from domain.common.events import DomainEvent


class UserCreatedEvent(DomainEvent):
    """Event raised when a new user is created."""
    
    user_id: str = Field(...)
    username: str = Field(...)
    email: str = Field(...)


class UserUpdatedEvent(DomainEvent):
    """Event raised when user information is updated."""
    
    user_id: str = Field(...)
    updated_fields: list[str] = Field(...)


class UserDeletedEvent(DomainEvent):
    """Event raised when a user is deleted."""
    
    user_id: str = Field(...)
    username: str = Field(...)


class UserPasswordChangedEvent(DomainEvent):
    """Event raised when user password is changed."""
    
    user_id: str = Field(...)