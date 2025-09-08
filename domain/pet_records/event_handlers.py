"""User domain event handlers."""

from loguru import logger

from domain.common.events import DomainEventHandler
from domain.pet_records.events import PetRecordCreatedEvent


class PetRecordCreatedEventHandler(DomainEventHandler):
    """Handler for pet record created events."""

    async def handle(self, event: PetRecordCreatedEvent) -> None:
        """Handle pet record created event."""
        logger.info(f"Pet record created: {event.pet_id} ({event.record_type})")
        # 这里可以添加更多逻辑，如：
        # - 发送通知
        # - 创建记录
        # - 设置默认偏好
        # - 发送到外部系统
