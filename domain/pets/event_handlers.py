"""Pet domain event handlers."""

from loguru import logger

from domain.common.events import DomainEventHandler
from domain.pets.events import (
    PetCreatedEvent,
    PetDeletedEvent,
    PetMorphologyUpdatedEvent,
    PetOwnershipChangedEvent,
)


class PetCreatedEventHandler(DomainEventHandler):
    """Handler for pet created events."""

    async def handle(self, event: PetCreatedEvent) -> None:
        """Handle pet created event."""
        logger.info(
            f"Pet created: {event.pet_id} for owner {event.owner_id} with breed {event.breed_id}"
        )
        # 这里可以添加更多逻辑，如：
        # - 发送欢迎通知
        # - 更新统计信息
        # - 创建默认配置
        # - 发送到外部系统


class PetOwnershipChangedEventHandler(DomainEventHandler):
    """Handler for pet ownership changed events."""

    async def handle(self, event: PetOwnershipChangedEvent) -> None:
        """Handle pet ownership changed event."""
        logger.info(
            f"Pet {event.pet_id} ownership changed from {event.old_owner_id} to {event.new_owner_id}"
        )
        # 这里可以添加更多逻辑，如：
        # - 更新所有权历史记录
        # - 通知新旧主人
        # - 更新权限和访问控制
        # - 发送所有权转移确认


class PetMorphologyUpdatedEventHandler(DomainEventHandler):
    """Handler for pet morphology updated events."""

    async def handle(self, event: PetMorphologyUpdatedEvent) -> None:
        """Handle pet morphology updated event."""
        logger.info(
            f"Pet {event.pet_id} morphology updated from {event.old_morphology_id} to {event.new_morphology_id}"
        )
        # 这里可以添加更多逻辑，如：
        # - 更新基因组合信息
        # - 重新计算兼容性
        # - 通知相关服务
        # - 更新显示信息


class PetDeletedEventHandler(DomainEventHandler):
    """Handler for pet deleted events."""

    async def handle(self, event: PetDeletedEvent) -> None:
        """Handle pet deleted event."""
        logger.info(f"Pet {event.pet_id} deleted by owner {event.owner_id}")
        # 这里可以添加更多逻辑，如：
        # - 清理相关数据
        # - 更新统计信息
        # - 发送删除确认
        # - 归档历史记录
