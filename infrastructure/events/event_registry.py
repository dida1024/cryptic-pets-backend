"""Event registry for registering domain event handlers."""

from domain.common.events import get_event_bus
from domain.pets.event_handlers import (
    PetCreatedEventHandler,
    PetDeletedEventHandler,
    PetMorphologyUpdatedEventHandler,
    PetOwnershipChangedEventHandler,
)
from domain.pets.events import (
    PetCreatedEvent,
    PetDeletedEvent,
    PetMorphologyUpdatedEvent,
    PetOwnershipChangedEvent,
)
from domain.users.event_handlers import UserCreatedEventHandler, UserUpdatedEventHandler
from domain.users.events import UserCreatedEvent, UserUpdatedEvent
from infrastructure.events.audit_event_handlers import (
    AuditEventHandler,
    PetAuditEventHandler,
    UserAuditEventHandler,
)
from infrastructure.events.notification_event_handlers import (
    EmailNotificationHandler,
    NotificationEventHandler,
    PushNotificationHandler,
)


def register_all_event_handlers() -> None:
    """Register all domain event handlers with the event bus."""
    event_bus = get_event_bus()

    # 注册宠物相关事件处理器
    event_bus.subscribe(PetCreatedEvent, PetCreatedEventHandler())
    event_bus.subscribe(PetOwnershipChangedEvent, PetOwnershipChangedEventHandler())
    event_bus.subscribe(PetMorphologyUpdatedEvent, PetMorphologyUpdatedEventHandler())
    event_bus.subscribe(PetDeletedEvent, PetDeletedEventHandler())

    # 注册用户相关事件处理器
    event_bus.subscribe(UserCreatedEvent, UserCreatedEventHandler())
    event_bus.subscribe(UserUpdatedEvent, UserUpdatedEventHandler())

    # 注册审计事件处理器
    event_bus.subscribe(PetCreatedEvent, AuditEventHandler())
    event_bus.subscribe(PetOwnershipChangedEvent, AuditEventHandler())
    event_bus.subscribe(PetMorphologyUpdatedEvent, AuditEventHandler())
    event_bus.subscribe(PetDeletedEvent, AuditEventHandler())
    event_bus.subscribe(UserCreatedEvent, AuditEventHandler())
    event_bus.subscribe(UserUpdatedEvent, AuditEventHandler())

    # 注册专门的审计处理器
    event_bus.subscribe(PetCreatedEvent, PetAuditEventHandler())
    event_bus.subscribe(PetOwnershipChangedEvent, PetAuditEventHandler())
    event_bus.subscribe(PetMorphologyUpdatedEvent, PetAuditEventHandler())
    event_bus.subscribe(PetDeletedEvent, PetAuditEventHandler())
    event_bus.subscribe(UserCreatedEvent, UserAuditEventHandler())
    event_bus.subscribe(UserUpdatedEvent, UserAuditEventHandler())

    # 注册通知事件处理器
    event_bus.subscribe(PetCreatedEvent, NotificationEventHandler())
    event_bus.subscribe(PetOwnershipChangedEvent, NotificationEventHandler())
    event_bus.subscribe(PetMorphologyUpdatedEvent, NotificationEventHandler())
    event_bus.subscribe(PetDeletedEvent, NotificationEventHandler())
    event_bus.subscribe(UserCreatedEvent, NotificationEventHandler())
    event_bus.subscribe(UserUpdatedEvent, NotificationEventHandler())

    # 注册邮件通知处理器
    event_bus.subscribe(PetCreatedEvent, EmailNotificationHandler())
    event_bus.subscribe(PetOwnershipChangedEvent, EmailNotificationHandler())
    event_bus.subscribe(UserCreatedEvent, EmailNotificationHandler())
    event_bus.subscribe(UserUpdatedEvent, EmailNotificationHandler())

    # 注册推送通知处理器
    event_bus.subscribe(PetCreatedEvent, PushNotificationHandler())
    event_bus.subscribe(PetOwnershipChangedEvent, PushNotificationHandler())
    event_bus.subscribe(UserCreatedEvent, PushNotificationHandler())
    event_bus.subscribe(UserUpdatedEvent, PushNotificationHandler())


def register_pet_event_handlers() -> None:
    """Register only pet-related event handlers."""
    event_bus = get_event_bus()

    event_bus.subscribe(PetCreatedEvent, PetCreatedEventHandler())
    event_bus.subscribe(PetOwnershipChangedEvent, PetOwnershipChangedEventHandler())
    event_bus.subscribe(PetMorphologyUpdatedEvent, PetMorphologyUpdatedEventHandler())
    event_bus.subscribe(PetDeletedEvent, PetDeletedEventHandler())


def register_user_event_handlers() -> None:
    """Register only user-related event handlers."""
    event_bus = get_event_bus()

    event_bus.subscribe(UserCreatedEvent, UserCreatedEventHandler())
    event_bus.subscribe(UserUpdatedEvent, UserUpdatedEventHandler())
