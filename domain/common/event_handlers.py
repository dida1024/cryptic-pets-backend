"""Example domain event handlers."""

from domain.common.events import DomainEventHandler, subscribe_to_event
from domain.pets.events import PetCreatedEvent, PetOwnershipChangedEvent
from domain.users.events import UserCreatedEvent


class PetCreatedEventHandler(DomainEventHandler):
    """Handler for pet created events."""
    
    async def handle(self, event: PetCreatedEvent) -> None:
        """Handle pet created event."""
        # Example: Log the event, update statistics, send notifications, etc.
        print(f"Pet created: {event.pet_id} for owner {event.owner_id}")


class PetOwnershipChangedEventHandler(DomainEventHandler):
    """Handler for pet ownership changed events."""
    
    async def handle(self, event: PetOwnershipChangedEvent) -> None:
        """Handle pet ownership changed event."""
        # Example: Update ownership history, notify users, etc.
        print(f"Pet {event.pet_id} ownership changed from {event.old_owner_id} to {event.new_owner_id}")


class UserCreatedEventHandler(DomainEventHandler):
    """Handler for user created events."""
    
    async def handle(self, event: UserCreatedEvent) -> None:
        """Handle user created event."""
        # Example: Send welcome email, create user profile, etc.
        print(f"User created: {event.username} ({event.email})")


# Example of using the decorator approach
@subscribe_to_event(PetCreatedEvent)
async def log_pet_creation(event: PetCreatedEvent) -> None:
    """Log pet creation using decorator approach."""
    print(f"[DECORATOR] Pet {event.pet_id} was created for breed {event.breed_id}")


@subscribe_to_event(UserCreatedEvent)
async def setup_user_profile(event: UserCreatedEvent) -> None:
    """Setup user profile using decorator approach."""
    print(f"[DECORATOR] Setting up profile for user {event.username}")


def register_event_handlers() -> None:
    """Register all event handlers with the event bus."""
    from domain.common.events import get_event_bus
    
    event_bus = get_event_bus()
    
    # Register class-based handlers
    event_bus.subscribe(PetCreatedEvent, PetCreatedEventHandler())
    event_bus.subscribe(PetOwnershipChangedEvent, PetOwnershipChangedEventHandler())
    event_bus.subscribe(UserCreatedEvent, UserCreatedEventHandler())
    
    # Decorator-based handlers are automatically registered