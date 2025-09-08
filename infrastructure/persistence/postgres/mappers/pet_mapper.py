
from loguru import logger

from domain.pets.entities import Pet
from infrastructure.persistence.postgres.mappers.base import BaseMapper
from infrastructure.persistence.postgres.mappers.breed_mapper import BreedMapper
from infrastructure.persistence.postgres.mappers.morph_gene_mapping_mapper import (
    MorphGeneMappingMapper,
)
from infrastructure.persistence.postgres.mappers.morphology_mapper import (
    MorphologyMapper,
)
from infrastructure.persistence.postgres.mappers.user_mapper import UserMapper
from infrastructure.persistence.postgres.models.pet import PetModel


class PetMapper(BaseMapper[Pet, PetModel]):
    """宠物实体与模型转换器"""

    def __init__(
        self,
        breed_mapper: BreedMapper,
        morphology_mapper: MorphologyMapper,
        gene_mapping_mapper: MorphGeneMappingMapper,
        user_mapper: UserMapper,
    ):
        self.breed_mapper = breed_mapper
        self.morphology_mapper = morphology_mapper
        self.gene_mapping_mapper = gene_mapping_mapper
        self.user_mapper = user_mapper

    def to_domain(self, model: PetModel) -> Pet:
        """数据库模型转换为领域实体"""
        logger.info(f"Converting pet model: {model}")

        # 转换额外基因列表
        extra_gene_list = []
        if model.extra_gene_list:
            extra_gene_list = [
                self.gene_mapping_mapper.to_domain(mapping)
                for mapping in model.extra_gene_list
            ]

        return Pet(
            id=model.id,
            name=model.name,
            description=model.description,
            birth_date=model.birth_date,
            owner_id=model.owner_id,
            breed_id=model.breed_id,
            gender=model.gender,
            extra_gene_list=extra_gene_list,
            morphology_id=model.morphology_id,
            picture_list=[],  # TODO: 实现图片转换逻辑
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_deleted=model.is_deleted,
        )

    def to_model(self, entity: Pet) -> PetModel:
        """领域实体转换为数据库模型"""
        return PetModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            birth_date=entity.birth_date,
            owner_id=entity.owner_id,
            breed_id=entity.breed_id,
            gender=entity.gender,
            morphology_id=entity.morphology_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_deleted=entity.is_deleted,
        )
