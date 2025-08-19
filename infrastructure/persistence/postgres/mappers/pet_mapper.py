
from domain.pets.entities import Pet
from domain.users.entities import User
from infrastructure.persistence.postgres.mappers.base import BaseMapper
from infrastructure.persistence.postgres.mappers.breed_mapper import BreedMapper
from infrastructure.persistence.postgres.mappers.morph_gene_mapping_mapper import (
    MorphGeneMappingMapper,
)
from infrastructure.persistence.postgres.mappers.morphology_mapper import (
    MorphologyMapper,
)
from infrastructure.persistence.postgres.models.pet import PetModel


class PetMapper(BaseMapper[Pet, PetModel]):
    """宠物实体与模型转换器"""

    def __init__(
        self,
        breed_mapper: BreedMapper,
        morphology_mapper: MorphologyMapper,
        gene_mapping_mapper: MorphGeneMappingMapper
    ):
        self.breed_mapper = breed_mapper
        self.morphology_mapper = morphology_mapper
        self.gene_mapping_mapper = gene_mapping_mapper

    def to_domain(self, model: PetModel) -> Pet:
        """数据库模型转换为领域实体"""
        # 转换品种
        breed = self.breed_mapper.to_domain(model.breed) if model.breed else None

        # 转换形态学
        morphology = None
        if model.morphology:
            morphology = self.morphology_mapper.to_domain(model.morphology)

        # 转换额外基因列表
        extra_gene_list = []
        if model.extra_gene_list:
            extra_gene_list = [
                self.gene_mapping_mapper.to_domain(mapping)
                for mapping in model.extra_gene_list
            ]

        # TODO: 需要从用户Repository获取owner信息
        # 这里暂时创建一个占位符，实际实现中需要通过依赖注入获取UserRepository
        owner = User(
            id=model.owner_id,
            username="",  # 需要从用户服务获取
            email="",     # 需要从用户服务获取
            created_at=None,
            updated_at=None,
            is_deleted=False,
            version=0
        )

        return Pet(
            id=model.id,
            name=model.name,
            birth_date=model.birth_date,
            owner=owner,
            breed=breed,
            gender=model.gender,
            extra_gene_list=extra_gene_list,
            morphology=morphology,
            picture_list=[],  # TODO: 实现图片转换逻辑
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_deleted=model.is_deleted,
            version=model.version
        )

    def to_model(self, entity: Pet) -> PetModel:
        """领域实体转换为数据库模型"""
        return PetModel(
            id=entity.id,
            name=entity.name,
            birth_date=entity.birth_date,
            owner_id=entity.owner.id,
            breed_id=entity.breed.id if entity.breed else None,
            gender=entity.gender,
            morphology_id=entity.morphology.id if entity.morphology else None,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_deleted=entity.is_deleted,
            version=entity.version
        )
