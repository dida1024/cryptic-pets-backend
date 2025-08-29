from domain.pets.entities import MorphGeneMapping
from infrastructure.persistence.postgres.mappers.base import BaseMapper
from infrastructure.persistence.postgres.mappers.gene_mapper import GeneMapper
from infrastructure.persistence.postgres.models.morph_gene_mapping import (
    MorphGeneMappingModel,
)


class MorphGeneMappingMapper(BaseMapper[MorphGeneMapping, MorphGeneMappingModel]):
    """基因映射实体与模型转换器"""

    def __init__(self, gene_mapper: GeneMapper):
        self.gene_mapper = gene_mapper

    def to_domain(self, model: MorphGeneMappingModel) -> MorphGeneMapping:
        """数据库模型转换为领域实体"""
        gene = self.gene_mapper.to_domain(model.gene) if model.gene else None

        return MorphGeneMapping(
            id=model.id,
            gene=gene,
            zygosity=model.zygosity,
            is_required=model.is_required,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_deleted=model.is_deleted,
        )

    def to_model(self, entity: MorphGeneMapping) -> MorphGeneMappingModel:
        """领域实体转换为数据库模型"""
        return MorphGeneMappingModel(
            id=entity.id,
            gene_id=entity.gene.id if entity.gene else None,
            zygosity=entity.zygosity,
            is_required=entity.is_required,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_deleted=entity.is_deleted,
        )
