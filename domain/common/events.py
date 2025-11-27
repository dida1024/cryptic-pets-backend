"""Domain events infrastructure for the application."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from loguru import logger
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


class EventBusProtocol(Protocol):
    """Protocol for event bus implementations.

    This protocol enables dependency injection and easier testing.
    """

    def subscribe(
        self, event_type: type[DomainEvent], handler: DomainEventHandler
    ) -> None:
        """Subscribe a handler to an event type."""
        ...

    def unsubscribe(
        self, event_type: type[DomainEvent], handler: DomainEventHandler
    ) -> None:
        """Unsubscribe a handler from an event type."""
        ...

    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all registered handlers."""
        ...

    async def publish_all(self, events: list[DomainEvent]) -> None:
        """Publish multiple events."""
        ...

    def clear_handlers(self) -> None:
        """Clear all registered handlers."""
        ...


class EventBus:
    """Event bus for publishing and subscribing to domain events.

    This class can be instantiated directly for testing or injected
    via dependency injection in production.
    """

    def __init__(self) -> None:
        """Initialize the event bus with an empty handlers registry."""
        self._handlers: dict[type[DomainEvent], list[DomainEventHandler]] = {}

    def subscribe(
        self, event_type: type[DomainEvent], handler: DomainEventHandler
    ) -> None:
        """Subscribe a handler to an event type.

        Args:
            event_type: The type of event to subscribe to.
            handler: The handler to be called when the event is published.
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.debug(
            f"Subscribed handler {handler.__class__.__name__} to {event_type.__name__}"
        )

    def unsubscribe(
        self, event_type: type[DomainEvent], handler: DomainEventHandler
    ) -> None:
        """Unsubscribe a handler from an event type.

        Args:
            event_type: The type of event to unsubscribe from.
            handler: The handler to remove.
        """
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                logger.debug(
                    f"Unsubscribed handler {handler.__class__.__name__} "
                    f"from {event_type.__name__}"
                )
            except ValueError:
                pass  # Handler not found, ignore

    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all registered handlers.

        Args:
            event: The domain event to publish.
        """
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])

        logger.debug(
            f"Publishing event {event.event_type} to {len(handlers)} handlers"
        )

        for handler in handlers:
            try:
                await handler.handle(event)
            except Exception as e:
                logger.error(
                    f"Error handling event {event.event_type} "
                    f"by {handler.__class__.__name__}: {e}"
                )

    async def publish_all(self, events: list[DomainEvent]) -> None:
        """Publish multiple events.

        Args:
            events: List of domain events to publish.
        """
        for event in events:
            await self.publish(event)

    def clear_handlers(self) -> None:
        """Clear all registered handlers."""
        self._handlers.clear()
        logger.debug("Cleared all event handlers")

    def get_handlers_count(self, event_type: type[DomainEvent] | None = None) -> int:
        """Get the count of registered handlers.

        Args:
            event_type: Optional event type to count handlers for.
                       If None, returns total count of all handlers.

        Returns:
            Number of registered handlers.
        """
        if event_type is not None:
            return len(self._handlers.get(event_type, []))
        return sum(len(handlers) for handlers in self._handlers.values())

    def has_handlers(self, event_type: type[DomainEvent]) -> bool:
        """Check if there are any handlers for an event type.

        Args:
            event_type: The event type to check.

        Returns:
            True if there are handlers registered for this event type.
        """
        return bool(self._handlers.get(event_type))


# ========== Global Instance (for backwards compatibility) ==========
# Note: Prefer using dependency injection instead of the global instance

_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance.

    This function is provided for backwards compatibility.
    In new code, prefer injecting EventBus via dependency injection.

    Returns:
        The global EventBus instance.
    """
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def reset_global_event_bus() -> None:
    """Reset the global event bus instance.

    This is useful for testing to ensure a clean state.
    """
    global _event_bus
    if _event_bus is not None:
        _event_bus.clear_handlers()
    _event_bus = EventBus()


def subscribe_to_event(event_type: type[DomainEvent]) -> Callable:
    """Decorator to subscribe a function as an event handler.

    Note: This uses the global event bus. For testability,
    consider using explicit subscription with injected EventBus.

    Args:
        event_type: The type of event to subscribe to.

    Returns:
        Decorator function.
    """

    def decorator(handler_func: Callable[[DomainEvent], None]) -> Callable:
        class FunctionHandler(DomainEventHandler):
            async def handle(self, event: DomainEvent) -> None:
                if callable(handler_func):
                    await handler_func(event)

        get_event_bus().subscribe(event_type, FunctionHandler())
        return handler_func

    return decorator
