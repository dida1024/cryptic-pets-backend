
from passlib.context import CryptContext

from application.users.commands import (
    CreateUserCommand,
    DeleteUserCommand,
    ListUsersQuery,
    UpdatePasswordCommand,
    UpdateUserCommand,
)
from domain.users.entities import User
from domain.users.exceptions import UserNotFoundError
from domain.users.repository import UserRepository


class UserService:
    """用户服务"""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def _hash_password(self, password: str) -> str:
        """哈希密码"""
        return self.pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(plain_password, hashed_password)

    async def create_user(self, command: CreateUserCommand) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        if await self.user_repository.exists_by_username(command.username):
            from domain.users.exceptions import DuplicateUsernameError
            raise DuplicateUsernameError(f"Username '{command.username}' already exists")

        # 检查邮箱是否已存在
        if await self.user_repository.exists_by_email(command.email):
            from domain.users.exceptions import DuplicateEmailError
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

        # 保存用户
        return await self.user_repository.create(user)

    async def get_user_by_id(self, user_id: str) -> User:
        """根据ID获取用户"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id '{user_id}' not found")
        return user

    async def get_user_by_username(self, username: str) -> User:
        """根据用户名获取用户"""
        user = await self.user_repository.get_by_username(username)
        if not user:
            raise UserNotFoundError(f"User with username '{username}' not found")
        return user

    async def get_user_by_email(self, email: str) -> User:
        """根据邮箱获取用户"""
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise UserNotFoundError(f"User with email '{email}' not found")
        return user

    async def update_user(self, command: UpdateUserCommand) -> User:
        """更新用户"""
        # 获取现有用户
        user = await self.get_user_by_id(command.user_id)

        # 检查用户名唯一性
        if command.username and command.username != user.username:
            if await self.user_repository.exists_by_username(command.username, exclude_id=user.id):
                from domain.users.exceptions import DuplicateUsernameError
                raise DuplicateUsernameError(f"Username '{command.username}' already exists")

        # 检查邮箱唯一性
        if command.email and command.email != user.email:
            if await self.user_repository.exists_by_email(command.email, exclude_id=user.id):
                from domain.users.exceptions import DuplicateEmailError
                raise DuplicateEmailError(f"Email '{command.email}' already exists")

        # 更新字段
        if command.username is not None:
            user.username = command.username
        if command.email is not None:
            user.email = command.email
        if command.full_name is not None:
            user.full_name = command.full_name
        if command.user_type is not None:
            user.user_type = command.user_type
        if command.is_active is not None:
            user.is_active = command.is_active

        # 更新时间戳
        user._update_timestamp()

        # 保存更新
        return await self.user_repository.update(user)

    async def update_password(self, command: UpdatePasswordCommand) -> User:
        """更新用户密码"""
        # 获取现有用户
        user = await self.get_user_by_id(command.user_id)

        # 验证当前密码
        if not self._verify_password(command.current_password, user.hashed_password):
            from domain.users.exceptions import InvalidCredentialsError
            raise InvalidCredentialsError("Current password is incorrect")

        # 更新密码
        user.hashed_password = self._hash_password(command.new_password)
        user._update_timestamp()

        # 保存更新
        return await self.user_repository.update(user)

    async def delete_user(self, command: DeleteUserCommand) -> bool:
        """删除用户（软删除）"""
        # 检查用户是否存在
        user = await self.user_repository.get_by_id(command.user_id)
        if not user:
            raise UserNotFoundError(f"User with id '{command.user_id}' not found")

        # 执行软删除
        return await self.user_repository.delete(command.user_id)

    async def list_users(self, query: ListUsersQuery) -> tuple[list[User], int]:
        """获取用户列表"""
        return await self.user_repository.list_users(
            page=query.page,
            page_size=query.page_size,
            search=query.search,
            user_type=query.user_type.value if query.user_type else None,
            is_active=query.is_active,
            include_deleted=query.include_deleted,
        )
