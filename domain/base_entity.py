from datetime import datetime
from typing import Any, List, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from domain.common.events import DomainEvent


class BaseEntity(BaseModel):
    """Base entity class for all domain entities."""

    id: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_deleted: bool = Field(default=False)

    model_config = ConfigDict(
        from_attributes=True,  # 支持从ORM模型创建
        validate_assignment=True,  # 在赋值时进行验证
        extra='forbid',  # 禁止额外字段
        arbitrary_types_allowed=True,  # 允许任意类型
        json_encoders={
            UUID: str  # UUID序列化为字符串
        }
    )

    def __init__(self, **data):
        super().__init__(**data)
        self._domain_events: List["DomainEvent"] = []

    def mark_as_deleted(self) -> None:
        """Mark the entity as deleted and update the updated_at timestamp."""
        self.is_deleted = True
        self._update_timestamp()

    def _update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now()

    def _add_domain_event(self, event: "DomainEvent") -> None:
        """Add a domain event to be published."""
        self._domain_events.append(event)

    def get_domain_events(self) -> List["DomainEvent"]:
        """Get all unpublished domain events."""
        return self._domain_events.copy()

    def clear_domain_events(self) -> None:
        """Clear all domain events after publishing."""
        self._domain_events.clear()

    def __eq__(self, other: Any) -> bool:
        """Entities are equal if their IDs are equal."""
        if not isinstance(other, BaseEntity):
            return NotImplemented
        return bool(self.id and other.id and self.id == other.id)

    def __hash__(self) -> int:
        """Hash based on entity ID."""
        return hash(self.id) if self.id else super().__hash__()

