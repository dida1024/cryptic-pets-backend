"""User domain event handlers."""

from loguru import logger

from domain.common.events import DomainEventHandler
from domain.users.events import UserCreatedEvent, UserUpdatedEvent


class UserCreatedEventHandler(DomainEventHandler):
    """Handler for user created events."""

    async def handle(self, event: UserCreatedEvent) -> None:
        """Handle user created event."""
        logger.info(f"User created: {event.username} ({event.email})")
        # 这里可以添加更多逻辑，如：
        # - 发送欢迎邮件
        # - 创建用户配置文件
        # - 设置默认偏好
        # - 发送到外部系统

class UserUpdatedEventHandler(DomainEventHandler):
    """Handler for user updated events."""

    async def handle(self, event: UserUpdatedEvent) -> None:
        """Handle user updated event."""
        logger.info(f"User {event.user_id} updated fields: {event.updated_fields}")
