"""Event publisher service for domain events."""

from typing import TYPE_CHECKING

from domain.common.events import get_event_bus

if TYPE_CHECKING:
    from domain.common.aggregate_root import AggregateRoot
    from domain.common.events import DomainEvent


class EventPublisher:
    """Service for publishing domain events from aggregate roots."""

    def __init__(self):
        self._event_bus = get_event_bus()

    async def publish_events_from_aggregate(self, aggregate: "AggregateRoot") -> None:
        """Publish all domain events from an aggregate root and clear them."""
        events = aggregate.get_domain_events()
        if events:
            await self._event_bus.publish_all(events)
            aggregate.clear_domain_events()

    async def publish_events_from_aggregates(self, aggregates: list["AggregateRoot"]) -> None:
        """Publish all domain events from multiple aggregate roots."""
        for aggregate in aggregates:
            await self.publish_events_from_aggregate(aggregate)

    async def publish_event(self, event: "DomainEvent") -> None:
        """Publish a single domain event directly."""
        await self._event_bus.publish(event)

    async def publish_events(self, events: list["DomainEvent"]) -> None:
        """Publish multiple domain events directly."""
        await self._event_bus.publish_all(events)


# Global event publisher instance
_event_publisher = EventPublisher()


def get_event_publisher() -> EventPublisher:
    """Get the global event publisher instance."""
    return _event_publisher
