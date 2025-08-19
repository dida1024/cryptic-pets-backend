
from domain.pets.entities import Breed
from infrastructure.persistence.postgres.mappers.base import BaseMapper
from infrastructure.persistence.postgres.models.breed import BreedModel


class BreedMapper(BaseMapper[Breed, BreedModel]):
    """品种实体与模型转换器"""

    def to_domain(self, model: BreedModel) -> Breed:
        """数据库模型转换为领域实体"""
        return Breed(
            id=model.id,
            name=model.name,
            description=model.description,
            picture_list=[],  # TODO: 实现图片转换逻辑
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_deleted=model.is_deleted,
            version=model.version
        )

    def to_model(self, entity: Breed) -> BreedModel:
        """领域实体转换为数据库模型"""
        return BreedModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_deleted=entity.is_deleted,
            version=entity.version
        )
