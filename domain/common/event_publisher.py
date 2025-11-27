"""Event publisher service for domain events."""

from typing import TYPE_CHECKING

from domain.common.events import EventBus, get_event_bus

if TYPE_CHECKING:
    from domain.common.aggregate_root import AggregateRoot
    from domain.common.events import DomainEvent


class EventPublisher:
    """Service for publishing domain events from aggregate roots.

    This class can be instantiated with a specific EventBus for testing,
    or it will use the provided/default event bus in production.
    """

    def __init__(self, event_bus: EventBus | None = None) -> None:
        """Initialize the event publisher.

        Args:
            event_bus: Optional EventBus instance. If not provided,
                      defaults to None and must be set later or will
                      use the global instance as fallback.
        """
        self._event_bus = event_bus

    @property
    def event_bus(self) -> EventBus:
        """Get the event bus instance.

        Returns:
            The EventBus instance, falling back to global if not set.
        """
        if self._event_bus is None:
            self._event_bus = get_event_bus()
        return self._event_bus

    async def publish_events_from_aggregate(self, aggregate: "AggregateRoot") -> None:
        """Publish all domain events from an aggregate root and clear them.

        Args:
            aggregate: The aggregate root containing domain events.
        """
        events = aggregate.get_domain_events()
        if events:
            await self.event_bus.publish_all(events)
            aggregate.clear_domain_events()

    async def publish_events_from_aggregates(
        self, aggregates: list["AggregateRoot"]
    ) -> None:
        """Publish all domain events from multiple aggregate roots.

        Args:
            aggregates: List of aggregate roots containing domain events.
        """
        for aggregate in aggregates:
            await self.publish_events_from_aggregate(aggregate)

    async def publish_event(self, event: "DomainEvent") -> None:
        """Publish a single domain event directly.

        Args:
            event: The domain event to publish.
        """
        await self.event_bus.publish(event)

    async def publish_events(self, events: list["DomainEvent"]) -> None:
        """Publish multiple domain events directly.

        Args:
            events: List of domain events to publish.
        """
        await self.event_bus.publish_all(events)


# ========== Global Instance (for backwards compatibility) ==========
# Note: Prefer using dependency injection instead of the global instance

_event_publisher: EventPublisher | None = None


def get_event_publisher() -> EventPublisher:
    """Get the global event publisher instance.

    This function is provided for backwards compatibility.
    In new code, prefer injecting EventPublisher via dependency injection.

    Returns:
        The global EventPublisher instance.
    """
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = EventPublisher()
    return _event_publisher


def create_event_publisher(event_bus: EventBus) -> EventPublisher:
    """Create a new EventPublisher with a specific EventBus.

    This is useful for testing or when you need a custom EventBus.

    Args:
        event_bus: The EventBus instance to use.

    Returns:
        A new EventPublisher instance.
    """
    return EventPublisher(event_bus)


def reset_global_event_publisher() -> None:
    """Reset the global event publisher instance.

    This is useful for testing to ensure a clean state.
    """
    global _event_publisher
    _event_publisher = EventPublisher()
