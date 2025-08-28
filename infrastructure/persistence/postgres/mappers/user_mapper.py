
from domain.users.entities import User
from infrastructure.persistence.postgres.mappers.base import BaseMapper
from infrastructure.persistence.postgres.models.user import UserModel


class UserMapper(BaseMapper[User, UserModel]):
    """用户实体与模型转换器"""

    def __init__(self):
        pass

    def to_entity(self, model: UserModel) -> User:
        """数据库模型转换为领域实体"""
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

    def to_model(self, entity: User) -> UserModel:
        """领域实体转换为数据库模型"""
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
