"""Audit event handlers for domain events."""

from datetime import datetime

from loguru import logger

from domain.common.events import DomainEvent, DomainEventHandler
from domain.pets.events import (
    PetCreatedEvent,
    PetDeletedEvent,
    PetMorphologyUpdatedEvent,
    PetOwnershipChangedEvent,
)
from domain.users.events import UserCreatedEvent


class AuditEventHandler(DomainEventHandler):
    """Generic audit event handler that logs all domain events."""

    async def handle(self, event: DomainEvent) -> None:
        """Handle any domain event for audit purposes."""
        audit_data = {
            "event_type": event.event_type,
            "event_id": event.event_id,
            "occurred_at": event.occurred_at.isoformat(),
            "event_version": event.event_version,
        }
        match event:
            case PetCreatedEvent():
                audit_data.update({
                    "pet_id": event.pet_id,
                    "owner_id": event.owner_id,
                    "breed_id": event.breed_id,
                    "action": "pet_created",
                })
            case PetOwnershipChangedEvent():
                audit_data.update({
                    "pet_id": event.pet_id,
                    "old_owner_id": event.old_owner_id,
                    "new_owner_id": event.new_owner_id,
                    "action": "pet_ownership_changed",
                })
            case PetMorphologyUpdatedEvent():
                audit_data.update({
                    "pet_id": event.pet_id,
                    "old_morphology_id": event.old_morphology_id,
                    "new_morphology_id": event.new_morphology_id,
                    "action": "pet_morphology_updated",
                })
            case PetDeletedEvent():
                audit_data.update({
                    "pet_id": event.pet_id,
                    "owner_id": event.owner_id,
                    "action": "pet_deleted",
                })
            case UserCreatedEvent():
                audit_data.update({
                    "username": event.username,
                    "email": event.email,
                    "action": "user_created",
                })

        logger.info("AUDIT_EVENT", extra=audit_data)


class PetAuditEventHandler(DomainEventHandler):
    """Specialized audit handler for pet-related events."""

    async def handle(self, event: DomainEvent) -> None:
        """Handle pet-related events for audit purposes."""
        if not isinstance(event, PetCreatedEvent | PetOwnershipChangedEvent | PetMorphologyUpdatedEvent | PetDeletedEvent):
            return

        audit_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event.event_type,
            "event_id": event.event_id,
            "pet_id": getattr(event, 'pet_id', None),
        }

        match event:
            case PetCreatedEvent():
                audit_record.update({
                    "action": "CREATE",
                    "details": f"Pet created for owner {event.owner_id} with breed {event.breed_id}",
                })
            case PetOwnershipChangedEvent():
                audit_record.update({
                    "action": "OWNERSHIP_CHANGE",
                    "details": f"Ownership changed from {event.old_owner_id} to {event.new_owner_id}",
                })
            case PetMorphologyUpdatedEvent():
                audit_record.update({
                    "action": "MORPHOLOGY_UPDATE",
                    "details": f"Morphology changed from {event.old_morphology_id} to {event.new_morphology_id}",
                })
            case PetDeletedEvent():
                audit_record.update({
                    "action": "DELETE",
                    "details": f"Pet deleted by owner {event.owner_id}",
                })

        # 在实际应用中，这里可以将审计记录保存到数据库或发送到外部审计系统
        logger.info("PET_AUDIT", extra=audit_record)


class UserAuditEventHandler(DomainEventHandler):
    """Specialized audit handler for user-related events."""

    async def handle(self, event: DomainEvent) -> None:
        """Handle user-related events for audit purposes."""
        if not isinstance(event, UserCreatedEvent):
            return

        audit_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event.event_type,
            "event_id": event.event_id,
            "action": "CREATE",
            "username": event.username,
            "email": event.email,
            "details": f"User account created for {event.username}",
        }

        # 在实际应用中，这里可以将审计记录保存到数据库或发送到外部审计系统
        logger.info("USER_AUDIT", extra=audit_record)
