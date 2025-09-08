"""Tests for domain events infrastructure."""

import pytest
from unittest.mock import AsyncMock
from pydantic import Field

from domain.common.events import DomainEvent, DomainEventHandler, EventBus
from domain.common.aggregate_root import AggregateRoot
from domain.common.event_publisher import EventPublisher
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
    
    @pytest.mark.anyio
    async def test_event_bus_publish_and_subscribe(self):
        """Test event bus publishing and subscription."""
        event_bus = EventBus()
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
    async def test_event_bus_multiple_handlers(self):
        """Test that multiple handlers can subscribe to the same event."""
        event_bus = EventBus()
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
    async def test_event_bus_unsubscribe(self):
        """Test unsubscribing handlers from events."""
        event_bus = EventBus()
        handler = TestEventHandler()
        
        # Subscribe and then unsubscribe
        event_bus.subscribe(TestEvent, handler)
        event_bus.unsubscribe(TestEvent, handler)
        
        # Publish event
        event = TestEvent(message="Test message")
        await event_bus.publish(event)
        
        # Handler should not receive the event
        assert len(handler.handled_events) == 0
    
    @pytest.mark.anyio
    async def test_event_publisher_with_aggregate(self):
        """Test event publisher with aggregate roots."""
        publisher = EventPublisher()
        aggregate = TestAggregate(name="Test")
        
        # Mock the event bus
        publisher._event_bus.publish_all = AsyncMock()
        
        # Add events to aggregate
        aggregate.do_something()
        aggregate.do_something()
        
        # Publish events
        await publisher.publish_events_from_aggregate(aggregate)
        
        # Verify events were published and cleared
        publisher._event_bus.publish_all.assert_called_once()
        assert not aggregate.has_domain_events()
    
    def test_pet_created_event(self):
        """Test pet created event creation."""
        event = PetCreatedEvent(
            pet_id="pet123",
            owner_id="owner456", 
            breed_id="breed789"
        )
        
        assert event.pet_id == "pet123"
        assert event.owner_id == "owner456"
        assert event.breed_id == "breed789"
        assert event.event_type == "PetCreatedEvent"