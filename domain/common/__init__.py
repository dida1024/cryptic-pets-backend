"""Domain common module exports."""

from .aggregate_root import AggregateRoot
from .event_handlers import register_event_handlers
from .event_publisher import EventPublisher, get_event_publisher
from .events import (
    DomainEvent,
    DomainEventHandler,
    EventBus,
    get_event_bus,
    subscribe_to_event,
)

__all__ = [
    "AggregateRoot",
    "DomainEvent",
    "DomainEventHandler",
    "EventBus",
    "get_event_bus",
    "subscribe_to_event",
    "EventPublisher",
    "get_event_publisher",
    "register_event_handlers",
]
