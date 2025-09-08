"""Event-aware repository base class for PostgreSQL implementations."""

from typing import TypeVar

from domain.common.event_publisher import EventPublisher
from domain.common.events import DomainEvent
from domain.common.repository import BaseRepository

T = TypeVar('T')


class EventAwareRepository(BaseRepository[T]):
    """Base class for repositories that publish domain events after successful persistence."""

    def __init__(self, event_publisher: EventPublisher):
        self.event_publisher = event_publisher

    async def _publish_events_from_entity(self, entity: T) -> None:
        """Publish domain events from an entity if it's an aggregate root."""
        if hasattr(entity, 'get_domain_events') and hasattr(entity, 'clear_domain_events'):
            await self.event_publisher.publish_events_from_aggregate(entity)

    async def _publish_events_from_entities(self, entities: list[T]) -> None:
        """Publish domain events from multiple entities."""
        for entity in entities:
            await self._publish_events_from_entity(entity)

    async def _publish_event(self, event: DomainEvent) -> None:
        """Publish a single domain event."""
        await self.event_publisher.publish_event(event)

    async def _publish_events(self, events: list[DomainEvent]) -> None:
        """Publish multiple domain events."""
        await self.event_publisher.publish_events(events)
