
from sqlalchemy import func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from domain.users.entities import User
from domain.users.repository import UserRepository
from domain.users.value_objects import UserTypeEnum
from infrastructure.persistence.postgres.init_db import async_engine
from infrastructure.persistence.postgres.models.user import UserModel


class PostgreSQLUserRepository(UserRepository):
    """PostgreSQL用户仓储实现"""

    def _model_to_entity(self, model: UserModel) -> User:
        """将数据库模型转换为领域实体"""
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            full_name=model.full_name,
            hashed_password=model.hashed_password,
            user_type=model.user_type,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_deleted=model.is_deleted,
        )

    def _entity_to_model(self, entity: User) -> UserModel:
        """将领域实体转换为数据库模型"""
        return UserModel(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            full_name=entity.full_name,
            hashed_password=entity.hashed_password,
            user_type=entity.user_type,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_deleted=entity.is_deleted,
        )

    async def get_by_id(self, user_id: str) -> User | None:
        """根据ID获取用户"""
        async with AsyncSession(async_engine) as session:
            statement = select(UserModel).where(
                UserModel.id == user_id,
                UserModel.is_deleted == False  # noqa: E712
            )
            result = await session.exec(statement)
            model = result.first()
            return self._model_to_entity(model) if model else None

    async def get_by_username(self, username: str) -> User | None:
        """根据用户名获取用户"""
        async with AsyncSession(async_engine) as session:
            statement = select(UserModel).where(
                UserModel.username == username,
                UserModel.is_deleted == False  # noqa: E712
            )
            result = await session.exec(statement)
            model = result.first()
            return self._model_to_entity(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        """根据邮箱获取用户"""
        async with AsyncSession(async_engine) as session:
            statement = select(UserModel).where(
                UserModel.email == email,
                UserModel.is_deleted == False  # noqa: E712
            )
            result = await session.exec(statement)
            model = result.first()
            return self._model_to_entity(model) if model else None

    async def create(self, user: User) -> User:
        """创建用户"""
        async with AsyncSession(async_engine) as session:
            model = self._entity_to_model(user)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._model_to_entity(model)

    async def update(self, user: User) -> User:
        """更新用户"""
        async with AsyncSession(async_engine) as session:
            statement = select(UserModel).where(UserModel.id == user.id)
            result = await session.exec(statement)
            existing_model = result.first()
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

            session.add(existing_model)
            await session.commit()
            await session.refresh(existing_model)
            return self._model_to_entity(existing_model)

    async def delete(self, user_id: str) -> bool:
        """删除用户（软删除）"""
        async with AsyncSession(async_engine) as session:
            statement = select(UserModel).where(
                UserModel.id == user_id,
                UserModel.is_deleted == False  # noqa: E712
            )
            result = await session.exec(statement)
            model = result.first()
            if not model:
                return False

            model.is_deleted = True
            session.add(model)
            await session.commit()
            return True

    async def list_users(
        self,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None,
        user_type: str | None = None,
        is_active: bool | None = None,
        include_deleted: bool = False,
    ) -> tuple[list[User], int]:
        """获取用户列表"""
        async with AsyncSession(async_engine) as session:
            # 构建查询
            statement = select(UserModel)

            # 基础过滤条件
            if not include_deleted:
                statement = statement.where(UserModel.is_deleted == False)  # noqa: E712

            # 搜索条件
            if search:
                statement = statement.where(
                    or_(
                        UserModel.username.ilike(f"%{search}%"),
                        UserModel.email.ilike(f"%{search}%"),
                        UserModel.full_name.ilike(f"%{search}%") if UserModel.full_name else False
                    )
                )

            # 用户类型过滤
            if user_type:
                statement = statement.where(UserModel.user_type == UserTypeEnum(user_type))

            # 激活状态过滤
            if is_active is not None:
                statement = statement.where(UserModel.is_active == is_active)

            # 获取总数
            count_statement = select(func.count()).select_from(statement.subquery())
            count_result = await session.exec(count_statement)
            total = count_result.one()

            # 分页
            offset = (page - 1) * page_size
            statement = statement.offset(offset).limit(page_size)

            # 排序
            statement = statement.order_by(UserModel.created_at.desc())

            # 执行查询
            result = await session.exec(statement)
            models = result.all()
            users = [self._model_to_entity(model) for model in models]

            return users, total

    async def exists_by_username(self, username: str, exclude_id: str | None = None) -> bool:
        """检查用户名是否存在"""
        async with AsyncSession(async_engine) as session:
            statement = select(UserModel).where(
                UserModel.username == username,
                UserModel.is_deleted == False  # noqa: E712
            )
            if exclude_id:
                statement = statement.where(UserModel.id != exclude_id)

            result = await session.exec(statement)
            model = result.first()
            return model is not None

    async def exists_by_email(self, email: str, exclude_id: str | None = None) -> bool:
        """检查邮箱是否存在"""
        async with AsyncSession(async_engine) as session:
            statement = select(UserModel).where(
                UserModel.email == email,
                UserModel.is_deleted == False  # noqa: E712
            )
            if exclude_id:
                statement = statement.where(UserModel.id != exclude_id)

            result = await session.exec(statement)
            model = result.first()
            return model is not None
