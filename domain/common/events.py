"""Domain events infrastructure for the application."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class DomainEvent(BaseModel, ABC):
    """Base class for all domain events."""

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    event_version: int = Field(default=1)

    model_config = ConfigDict(frozen=True)  # Events are immutable

    @property
    def event_type(self) -> str:
        """Return the event type name."""
        return self.__class__.__name__


class DomainEventHandler(ABC):
    """Base class for domain event handlers."""

    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """Handle the domain event."""
        pass


class EventBus:
    """Event bus for publishing and subscribing to domain events."""

    def __init__(self):
        self._handlers: dict[type[DomainEvent], list[DomainEventHandler]] = {}

    def subscribe(self, event_type: type[DomainEvent], handler: DomainEventHandler) -> None:
        """Subscribe a handler to an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: type[DomainEvent], handler: DomainEventHandler) -> None:
        """Unsubscribe a handler from an event type."""
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
            except ValueError:
                pass  # Handler not found, ignore

    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all registered handlers."""
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])

        for handler in handlers:
            try:
                await handler.handle(event)
            except Exception as e:
                # Log error but don't stop other handlers
                # In a real application, you'd use proper logging
                print(f"Error handling event {event.event_type}: {e}")

    async def publish_all(self, events: list[DomainEvent]) -> None:
        """Publish multiple events."""
        for event in events:
            await self.publish(event)

    def clear_handlers(self) -> None:
        """Clear all registered handlers."""
        self._handlers.clear()


# Global event bus instance
_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    return _event_bus


def subscribe_to_event(event_type: type[DomainEvent]) -> Callable:
    """Decorator to subscribe a function as an event handler."""
    def decorator(handler_func: Callable[[DomainEvent], None]) -> Callable:
        class FunctionHandler(DomainEventHandler):
            async def handle(self, event: DomainEvent) -> None:
                if callable(handler_func):
                    await handler_func(event)

        _event_bus.subscribe(event_type, FunctionHandler())
        return handler_func

    return decorator
