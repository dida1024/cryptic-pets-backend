"""
用户命令处理器
实现CQRS模式的命令部分，处理写操作
"""

from uuid import uuid4

from loguru import logger
from passlib.context import CryptContext

from application.users.commands import (
    CreateUserCommand,
    DeleteUserCommand,
    UpdatePasswordCommand,
    UpdateUserCommand,
)
from domain.users.entities import User
from domain.users.exceptions import (
    DuplicateEmailError,
    DuplicateUsernameError,
    InvalidCredentialsError,
    UserNotFoundError,
)
from domain.users.repository import UserRepository


class CreateUserHandler:
    """创建用户命令处理器"""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.logger = logger

    def _hash_password(self, password: str) -> str:
        """哈希密码"""
        return self.pwd_context.hash(password)

    async def handle(self, command: CreateUserCommand) -> User:
        """处理创建用户命令"""
        # 检查用户名是否已存在
        if await self.user_repository.exists_by_username(command.username):
            raise DuplicateUsernameError(f"Username '{command.username}' already exists")

        # 检查邮箱是否已存在
        if await self.user_repository.exists_by_email(command.email):
            raise DuplicateEmailError(f"Email '{command.email}' already exists")

        # 创建用户实体
        user = User(
            username=command.username,
            email=command.email,
            full_name=command.full_name,
            hashed_password=self._hash_password(command.password),
            user_type=command.user_type,
            is_active=command.is_active,
        )
        if not user.id:
            user.id = str(uuid4())

        self.logger.info(f"Creating user: {user.username}")

        # 添加领域事件（在持久化之前，以便仓储统一发布）
        from domain.users.events import UserCreatedEvent
        user._add_domain_event(UserCreatedEvent(
            user_id=user.id,
            username=user.username,
            email=user.email,
        ))

        # 保存用户（仓储负责发布领域事件）
        return await self.user_repository.create(user)


class UpdateUserHandler:
    """更新用户命令处理器"""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.logger = logger

    async def handle(self, command: UpdateUserCommand) -> User:
        """处理更新用户命令"""
        # 获取现有用户
        if not (user := await self.user_repository.get_by_id(command.user_id)):
            raise UserNotFoundError(f"User with id '{command.user_id}' not found")

        # 检查用户名唯一性
        if command.username and command.username != user.username:
            if await self.user_repository.exists_by_username(command.username, exclude_id=user.id):
                raise DuplicateUsernameError(f"Username '{command.username}' already exists")

        # 检查邮箱唯一性
        if command.email and command.email != user.email:
            if await self.user_repository.exists_by_email(command.email, exclude_id=user.id):
                raise DuplicateEmailError(f"Email '{command.email}' already exists")

        # 更新字段
        updated_fields = []
        if command.username is not None:
            user.username = command.username
            updated_fields.append("username")
        if command.email is not None:
            user.email = command.email
            updated_fields.append("email")
        if command.full_name is not None:
            user.full_name = command.full_name
            updated_fields.append("full_name")
        if command.user_type is not None:
            user.user_type = command.user_type
            updated_fields.append("user_type")
        if command.is_active is not None:
            user.is_active = command.is_active
            updated_fields.append("is_active")

        user._update_timestamp()

        self.logger.info(f"Updating user: {user.username}")

        from domain.users.events import UserUpdatedEvent
        user._add_domain_event(UserUpdatedEvent(
            user_id=user.id,
            updated_fields=updated_fields,
        ))

        return await self.user_repository.update(user)


class UpdatePasswordHandler:
    """更新密码命令处理器"""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.logger = logger

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def _hash_password(self, password: str) -> str:
        """哈希密码"""
        return self.pwd_context.hash(password)

    async def handle(self, command: UpdatePasswordCommand) -> User:
        """处理更新密码命令"""
        # 获取现有用户
        user = await self.user_repository.get_by_id(command.user_id)
        if not user:
            raise UserNotFoundError(f"User with id '{command.user_id}' not found")

        # 验证当前密码
        if not self._verify_password(command.current_password, user.hashed_password):
            raise InvalidCredentialsError("Current password is incorrect")

        # 更新密码
        user.hashed_password = self._hash_password(command.new_password)
        user._update_timestamp()

        self.logger.info(f"Updating password for user: {user.username}")

        from domain.users.events import UserPasswordChangedEvent
        user._add_domain_event(UserPasswordChangedEvent(
            user_id=user.id,
        ))

        return await self.user_repository.update(user)


class DeleteUserHandler:
    """删除用户命令处理器"""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.logger = logger

    async def handle(self, command: DeleteUserCommand) -> bool:
        """处理删除用户命令"""
        # 检查用户是否存在
        user = await self.user_repository.get_by_id(command.user_id)
        if not user:
            raise UserNotFoundError(f"User with id '{command.user_id}' not found")

        self.logger.info(f"Deleting user: {user.username}")

        # 软删除并挂载领域事件
        user.mark_as_deleted()
        from domain.users.events import UserDeletedEvent
        user._add_domain_event(UserDeletedEvent(
            user_id=user.id,
            username=user.username,
        ))

        # 仓储负责执行软删除并发布领域事件
        return await self.user_repository.delete(user)
