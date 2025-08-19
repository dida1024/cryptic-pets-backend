
from domain.pets.entities import Morphology
from infrastructure.persistence.postgres.mappers.base import BaseMapper
from infrastructure.persistence.postgres.mappers.morph_gene_mapping_mapper import (
    MorphGeneMappingMapper,
)
from infrastructure.persistence.postgres.models.morphology import MorphologyModel


class MorphologyMapper(BaseMapper[Morphology, MorphologyModel]):
    """形态学实体与模型转换器"""

    def __init__(self, gene_mapping_mapper: MorphGeneMappingMapper):
        self.gene_mapping_mapper = gene_mapping_mapper

    def to_domain(self, model: MorphologyModel) -> Morphology:
        """数据库模型转换为领域实体"""
        gene_mappings = []
        if model.gene_mappings:
            gene_mappings = [
                self.gene_mapping_mapper.to_domain(mapping)
                for mapping in model.gene_mappings
            ]

        return Morphology(
            id=model.id,
            name=model.name,
            description=model.description,
            gene_mappings=gene_mappings,
            picture_list=[],  # TODO: 实现图片转换逻辑
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_deleted=model.is_deleted,
            version=model.version
        )

    def to_model(self, entity: Morphology) -> MorphologyModel:
        """领域实体转换为数据库模型"""
        return MorphologyModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_deleted=entity.is_deleted,
            version=entity.version
        )
