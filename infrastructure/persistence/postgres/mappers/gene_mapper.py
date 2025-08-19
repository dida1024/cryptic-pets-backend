from domain.pets.entities import Gene
from infrastructure.persistence.postgres.mappers.base import BaseMapper
from infrastructure.persistence.postgres.models.gene import GeneModel


class GeneMapper(BaseMapper[Gene, GeneModel]):
    """基因实体与模型转换器"""

    def to_domain(self, model: GeneModel) -> Gene:
        """数据库模型转换为领域实体"""
        return Gene(
            id=model.id,
            name=model.name,
            alias=model.alias,
            description=model.description,
            notation=model.notation,
            inheritance_type=model.inheritance_type,
            category=model.category,
            picture_list=[],  # TODO: 实现图片转换逻辑
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_deleted=model.is_deleted,
            version=model.version
        )

    def to_model(self, entity: Gene) -> GeneModel:
        """领域实体转换为数据库模型"""
        return GeneModel(
            id=entity.id,
            name=entity.name,
            alias=entity.alias,
            description=entity.description,
            notation=entity.notation,
            inheritance_type=entity.inheritance_type,
            category=entity.category,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_deleted=entity.is_deleted,
            version=entity.version
        )
