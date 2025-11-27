"""Tests for domain events infrastructure."""

from unittest.mock import AsyncMock

import pytest
from pydantic import Field

from domain.common.aggregate_root import AggregateRoot
from domain.common.event_publisher import EventPublisher, create_event_publisher
from domain.common.events import DomainEvent, DomainEventHandler, EventBus
from domain.pets.events import PetCreatedEvent


class TestEvent(DomainEvent):
    """Test event for testing purposes."""

    message: str = Field(...)


class TestEventHandler(DomainEventHandler):
    """Test event handler."""

    def __init__(self):
        self.handled_events = []

    async def handle(self, event: DomainEvent) -> None:
        self.handled_events.append(event)


class TestAggregate(AggregateRoot):
    """Test aggregate for testing domain events."""

    name: str = Field(...)

    def do_something(self) -> None:
        """Perform an action that raises a domain event."""
        event = TestEvent(message=f"Something happened to {self.name}")
        self.add_domain_event(event)


class TestDomainEvents:
    """Test cases for domain events infrastructure."""

    def test_domain_event_creation(self):
        """Test that domain events can be created with proper attributes."""
        event = TestEvent(message="Test message")

        assert event.message == "Test message"
        assert event.event_type == "TestEvent"
        assert event.event_id is not None
        assert event.occurred_at is not None
        assert event.event_version == 1

    def test_aggregate_root_domain_events(self):
        """Test that aggregate roots can manage domain events."""
        aggregate = TestAggregate(name="Test")

        # Initially no events
        assert not aggregate.has_domain_events()
        assert aggregate.get_domain_events_count() == 0
        assert len(aggregate.get_domain_events()) == 0

        # Add an event
        aggregate.do_something()

        # Should have one event
        assert aggregate.has_domain_events()
        assert aggregate.get_domain_events_count() == 1

        events = aggregate.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], TestEvent)
        assert events[0].message == "Something happened to Test"

        # Clear events
        aggregate.clear_domain_events()
        assert not aggregate.has_domain_events()
        assert aggregate.get_domain_events_count() == 0


class TestEventBus:
    """Test cases for EventBus."""

    @pytest.fixture
    def event_bus(self):
        """Create an isolated EventBus for testing."""
        return EventBus()

    @pytest.mark.anyio
    async def test_publish_and_subscribe(self, event_bus):
        """Test event bus publishing and subscription."""
        handler = TestEventHandler()

        # Subscribe handler
        event_bus.subscribe(TestEvent, handler)

        # Publish event
        event = TestEvent(message="Test message")
        await event_bus.publish(event)

        # Verify handler received the event
        assert len(handler.handled_events) == 1
        assert handler.handled_events[0] == event

    @pytest.mark.anyio
    async def test_multiple_handlers(self, event_bus):
        """Test that multiple handlers can subscribe to the same event."""
        handler1 = TestEventHandler()
        handler2 = TestEventHandler()

        # Subscribe both handlers
        event_bus.subscribe(TestEvent, handler1)
        event_bus.subscribe(TestEvent, handler2)

        # Publish event
        event = TestEvent(message="Test message")
        await event_bus.publish(event)

        # Both handlers should receive the event
        assert len(handler1.handled_events) == 1
        assert len(handler2.handled_events) == 1
        assert handler1.handled_events[0] == event
        assert handler2.handled_events[0] == event

    @pytest.mark.anyio
    async def test_unsubscribe(self, event_bus):
        """Test unsubscribing handlers from events."""
        handler = TestEventHandler()

        # Subscribe and then unsubscribe
        event_bus.subscribe(TestEvent, handler)
        event_bus.unsubscribe(TestEvent, handler)

        # Publish event
        event = TestEvent(message="Test message")
        await event_bus.publish(event)

        # Handler should not receive the event
        assert len(handler.handled_events) == 0

    def test_get_handlers_count(self, event_bus):
        """Test getting handler count."""
        handler1 = TestEventHandler()
        handler2 = TestEventHandler()

        assert event_bus.get_handlers_count() == 0
        assert event_bus.get_handlers_count(TestEvent) == 0

        event_bus.subscribe(TestEvent, handler1)
        assert event_bus.get_handlers_count() == 1
        assert event_bus.get_handlers_count(TestEvent) == 1

        event_bus.subscribe(TestEvent, handler2)
        assert event_bus.get_handlers_count() == 2
        assert event_bus.get_handlers_count(TestEvent) == 2

    def test_has_handlers(self, event_bus):
        """Test checking for handlers."""
        handler = TestEventHandler()

        assert not event_bus.has_handlers(TestEvent)

        event_bus.subscribe(TestEvent, handler)
        assert event_bus.has_handlers(TestEvent)

        event_bus.unsubscribe(TestEvent, handler)
        assert not event_bus.has_handlers(TestEvent)

    def test_clear_handlers(self, event_bus):
        """Test clearing all handlers."""
        handler = TestEventHandler()

        event_bus.subscribe(TestEvent, handler)
        assert event_bus.get_handlers_count() == 1

        event_bus.clear_handlers()
        assert event_bus.get_handlers_count() == 0

    @pytest.mark.anyio
    async def test_publish_all(self, event_bus):
        """Test publishing multiple events."""
        handler = TestEventHandler()
        event_bus.subscribe(TestEvent, handler)

        events = [
            TestEvent(message="Message 1"),
            TestEvent(message="Message 2"),
            TestEvent(message="Message 3"),
        ]

        await event_bus.publish_all(events)

        assert len(handler.handled_events) == 3


class TestEventPublisher:
    """Test cases for EventPublisher."""

    @pytest.fixture
    def event_bus(self):
        """Create an isolated EventBus for testing."""
        return EventBus()

    @pytest.fixture
    def publisher(self, event_bus):
        """Create an EventPublisher with injected EventBus."""
        return EventPublisher(event_bus)

    @pytest.mark.anyio
    async def test_publish_events_from_aggregate(self, publisher, event_bus):
        """Test publishing events from aggregate root."""
        handler = TestEventHandler()
        event_bus.subscribe(TestEvent, handler)

        aggregate = TestAggregate(name="Test")
        aggregate.do_something()
        aggregate.do_something()

        await publisher.publish_events_from_aggregate(aggregate)

        # Verify events were published
        assert len(handler.handled_events) == 2
        # Verify events were cleared from aggregate
        assert not aggregate.has_domain_events()

    @pytest.mark.anyio
    async def test_publish_event(self, publisher, event_bus):
        """Test publishing a single event directly."""
        handler = TestEventHandler()
        event_bus.subscribe(TestEvent, handler)

        event = TestEvent(message="Direct event")
        await publisher.publish_event(event)

        assert len(handler.handled_events) == 1
        assert handler.handled_events[0] == event

    @pytest.mark.anyio
    async def test_publish_events(self, publisher, event_bus):
        """Test publishing multiple events directly."""
        handler = TestEventHandler()
        event_bus.subscribe(TestEvent, handler)

        events = [
            TestEvent(message="Event 1"),
            TestEvent(message="Event 2"),
        ]
        await publisher.publish_events(events)

        assert len(handler.handled_events) == 2

    @pytest.mark.anyio
    async def test_create_event_publisher_helper(self):
        """Test the create_event_publisher helper function."""
        event_bus = EventBus()
        publisher = create_event_publisher(event_bus)

        assert publisher.event_bus is event_bus

    @pytest.mark.anyio
    async def test_publisher_with_mock_event_bus(self):
        """Test publisher with a mocked event bus."""
        mock_bus = AsyncMock(spec=EventBus)
        publisher = EventPublisher(mock_bus)

        aggregate = TestAggregate(name="Test")
        aggregate.do_something()

        await publisher.publish_events_from_aggregate(aggregate)

        mock_bus.publish_all.assert_called_once()


class TestEventBusIsolation:
    """Test cases to verify EventBus instances are properly isolated."""

    @pytest.mark.anyio
    async def test_separate_event_buses_are_isolated(self):
        """Test that separate EventBus instances don't share state."""
        bus1 = EventBus()
        bus2 = EventBus()

        handler1 = TestEventHandler()
        handler2 = TestEventHandler()

        bus1.subscribe(TestEvent, handler1)
        bus2.subscribe(TestEvent, handler2)

        event = TestEvent(message="Test")

        # Publish to bus1 only
        await bus1.publish(event)

        assert len(handler1.handled_events) == 1
        assert len(handler2.handled_events) == 0

        # Publish to bus2 only
        await bus2.publish(event)

        assert len(handler1.handled_events) == 1
        assert len(handler2.handled_events) == 1

    @pytest.mark.anyio
    async def test_publishers_with_different_buses(self):
        """Test that publishers with different buses are isolated."""
        bus1 = EventBus()
        bus2 = EventBus()

        publisher1 = EventPublisher(bus1)
        publisher2 = EventPublisher(bus2)

        handler1 = TestEventHandler()
        handler2 = TestEventHandler()

        bus1.subscribe(TestEvent, handler1)
        bus2.subscribe(TestEvent, handler2)

        aggregate1 = TestAggregate(name="Test1")
        aggregate1.do_something()

        aggregate2 = TestAggregate(name="Test2")
        aggregate2.do_something()

        # Publish from publisher1
        await publisher1.publish_events_from_aggregate(aggregate1)

        assert len(handler1.handled_events) == 1
        assert len(handler2.handled_events) == 0

        # Publish from publisher2
        await publisher2.publish_events_from_aggregate(aggregate2)

        assert len(handler1.handled_events) == 1
        assert len(handler2.handled_events) == 1


class TestPetCreatedEvent:
    """Test cases for specific domain events."""

    def test_pet_created_event_creation(self):
        """Test pet created event creation."""
        event = PetCreatedEvent(
            pet_id="pet123", owner_id="owner456", breed_id="breed789"
        )

        assert event.pet_id == "pet123"
        assert event.owner_id == "owner456"
        assert event.breed_id == "breed789"
        assert event.event_type == "PetCreatedEvent"
