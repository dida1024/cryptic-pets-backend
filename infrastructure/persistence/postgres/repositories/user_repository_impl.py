from loguru import logger
from sqlalchemy import func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from domain.users.entities import User
from domain.users.repository import UserRepository
from domain.users.value_objects import UserTypeEnum
from infrastructure.persistence.postgres.mappers.user_mapper import UserMapper
from infrastructure.persistence.postgres.models.user import UserModel


class PostgreSQLUserRepositoryImpl(UserRepository):
    """PostgreSQL用户仓储实现"""

    def __init__(self, session: AsyncSession, mapper: UserMapper):
        self.session = session
        self.mapper = mapper
        self.logger = logger

    async def get_by_id(self, user_id: str) -> User | None:
        """根据ID获取用户"""
        statement = select(UserModel).where(
            UserModel.id == user_id,
            UserModel.is_deleted.is_(False),
        )
        result = await self.session.execute(statement)
        model = result.scalar_one_or_none()
        return self.mapper.to_domain(model) if model else None

    async def get_by_username(self, username: str) -> User | None:
        """根据用户名获取用户"""
        statement = select(UserModel).where(
            UserModel.username == username,
            UserModel.is_deleted.is_(False),
        )
        result = await self.session.execute(statement)
        model = result.scalar_one_or_none()
        return self.mapper.to_domain(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        """根据邮箱获取用户"""
        statement = select(UserModel).where(
            UserModel.email == email,
            UserModel.is_deleted.is_(False),
        )
        result = await self.session.execute(statement)
        model = result.scalar_one_or_none()
        return self.mapper.to_domain(model) if model else None

    async def create(self, user: User) -> User:
        """创建用户"""
        model = self.mapper.to_model(user)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self.mapper.to_domain(model)

    async def update(self, user: User) -> User:
        """更新用户"""
        statement = select(UserModel).where(UserModel.id == user.id)
        result = await self.session.execute(statement)
        existing_model = result.scalar_one_or_none()
        if not existing_model:
            raise ValueError(f"User with id {user.id} not found")

        # 更新字段
        existing_model.username = user.username
        existing_model.email = user.email
        existing_model.full_name = user.full_name
        existing_model.hashed_password = user.hashed_password
        existing_model.user_type = user.user_type
        existing_model.is_active = user.is_active
        existing_model.updated_at = user.updated_at
        existing_model.is_deleted = user.is_deleted

        self.session.add(existing_model)
        await self.session.flush()
        await self.session.refresh(existing_model)
        return self.mapper.to_domain(existing_model)

    async def delete(self, user_id: str) -> bool:
        """删除用户（软删除）"""
        statement = select(UserModel).where(
            UserModel.id == user_id,
            UserModel.is_deleted.is_(False),
        )
        result = await self.session.execute(statement)
        model = result.scalar_one_or_none()
        if not model:
            return False

        model.is_deleted = True
        self.session.add(model)
        await self.session.flush()
        return True

    async def list_all(
        self,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None,
        user_type: str | None = None,
        is_active: bool | None = None,
        include_deleted: bool = False,
    ) -> tuple[list[User], int]:
        """获取用户列表"""
        statement = select(UserModel)

        if not include_deleted:
            statement = statement.where(UserModel.is_deleted.is_(False))

        if search:
            statement = statement.where(
                or_(
                    UserModel.username.ilike(f"%{search}%"),
                    UserModel.email.ilike(f"%{search}%"),
                    UserModel.full_name.ilike(f"%{search}%"),
                )
            )
        if user_type:
            statement = statement.where(
                UserModel.user_type == UserTypeEnum(user_type)
            )
        if is_active is not None:
            statement = statement.where(UserModel.is_active == is_active)

        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await self.session.execute(count_statement)
        total = count_result.scalar_one()

        offset = (page - 1) * page_size
        statement = statement.offset(offset).limit(page_size)
        statement = statement.order_by(UserModel.created_at.desc())

        result = await self.session.execute(statement)
        models = result.scalars().all()
        users = [self.mapper.to_domain(model) for model in models]

        return users, total

    async def exists_by_username(
        self, username: str, exclude_id: str | None = None
    ) -> bool:
        """检查用户名是否存在"""
        statement = select(UserModel).where(
            UserModel.username == username,
            UserModel.is_deleted.is_(False),
        )
        if exclude_id:
            statement = statement.where(UserModel.id != exclude_id)

        result = await self.session.execute(statement)
        model = result.scalar_one_or_none()
        return model is not None

    async def exists_by_email(self, email: str, exclude_id: str | None = None) -> bool:
        """检查邮箱是否存在"""
        statement = select(UserModel).where(
            UserModel.email == email,
            UserModel.is_deleted.is_(False),
        )
        if exclude_id:
            statement = statement.where(UserModel.id != exclude_id)

        result = await self.session.execute(statement)
        model = result.scalar_one_or_none()
        return model is not None
