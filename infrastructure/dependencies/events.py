"""Event dependency module.

Provides event bus and event publisher dependencies.
"""

from domain.common.event_publisher import EventPublisher
from domain.common.events import EventBus

# Use a singleton pattern that can be reset for testing
_event_bus_instance: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get the event bus instance.

    Returns a singleton EventBus instance. The instance can be reset
    using reset_event_bus() for testing purposes.

    Returns:
        EventBus: The event bus instance.
    """
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus()
    return _event_bus_instance


def get_event_publisher() -> EventPublisher:
    """Get the event publisher instance.

    Returns an EventPublisher that uses the injected EventBus.

    Returns:
        EventPublisher: The event publisher instance.
    """
    return EventPublisher(get_event_bus())


def reset_event_bus() -> None:
    """Reset the event bus instance.

    This clears all handlers and creates a fresh EventBus.
    Useful for testing to ensure a clean state.
    """
    global _event_bus_instance
    if _event_bus_instance is not None:
        _event_bus_instance.clear_handlers()
    _event_bus_instance = EventBus()


def create_test_event_bus() -> EventBus:
    """Create a new isolated EventBus for testing.

    Returns:
        EventBus: A fresh EventBus instance isolated from the global one.
    """
    return EventBus()


def create_test_event_publisher(event_bus: EventBus | None = None) -> EventPublisher:
    """Create a new EventPublisher for testing.

    Args:
        event_bus: Optional EventBus to use. If not provided,
                  creates a new isolated EventBus.

    Returns:
        EventPublisher: A new EventPublisher instance.
    """
    if event_bus is None:
        event_bus = create_test_event_bus()
    return EventPublisher(event_bus)

