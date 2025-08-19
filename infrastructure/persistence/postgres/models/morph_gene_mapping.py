from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    Enum,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
)
from sqlmodel import Field, Relationship

from domain.pets.value_objects import ZygosityEnum
from infrastructure.persistence.postgres.models.base import BaseModel
from infrastructure.persistence.postgres.models.gene import GeneModel

if TYPE_CHECKING:
    from infrastructure.persistence.postgres.models.morphology import MorphologyModel
    from infrastructure.persistence.postgres.models.pet import PetModel


class MorphGeneMappingModel(BaseModel, table=True):
    """MorphGeneMapping model representing gene mapping in the database.

    This table serves two purposes:
    1. Morphology-Gene relationship: defines which genes form a morphology (morphology_id + gene_id)
    2. Pet-Gene relationship: records extra genes expressed by individual pets (pet_id + gene_id)
    """

    __tablename__ = "morph_gene_mappings"

    gene_id: str = Field(
        sa_column=Column(String, ForeignKey("genes.id"), nullable=False),
        description="Foreign key to gene"
    )
    morphology_id: str | None = Field(
        sa_column=Column(String, ForeignKey("morphologies.id"), nullable=True),
        description="Foreign key to morphology (null for pet-specific genes)"
    )
    pet_id: str | None = Field(
        sa_column=Column(String, ForeignKey("pets.id"), nullable=True),
        description="Foreign key to pet (null for morphology definition)"
    )
    zygosity: ZygosityEnum = Field(
        sa_column=Column(Enum(ZygosityEnum), nullable=False, default=ZygosityEnum.UNKNOWN),
        description="Zygosity type"
    )
    is_required: bool = Field(
        sa_column=Column(Boolean, nullable=False, default=True),
        description="Is this gene required for the morphology/pet expression"
    )

    # 数据库约束和索引
    __table_args__ = (
        # 确保每条记录要么属于morphology要么属于pet，不能两者都为空
        # 这个约束需要通过应用层或数据库触发器来实现，SQLAlchemy不直接支持这种约束

        # 唯一约束：防止morphology重复添加相同基因
        UniqueConstraint('morphology_id', 'gene_id', name='unique_morphology_gene'),
        # 唯一约束：防止宠物重复添加相同基因
        UniqueConstraint('pet_id', 'gene_id', name='unique_pet_gene'),

        # 索引：优化根据形态学ID查询基因的性能
        Index('idx_morphology_genes', 'morphology_id'),
        # 索引：优化根据宠物ID查询额外基因的性能
        Index('idx_pet_extra_genes', 'pet_id'),
        # 索引：优化根据基因ID查询的性能
        Index('idx_gene_mappings', 'gene_id'),
        # 复合索引：优化按杂合性查询的性能
        Index('idx_morphology_gene_zygosity', 'morphology_id', 'zygosity'),
        Index('idx_pet_gene_zygosity', 'pet_id', 'zygosity'),
    )

    gene: GeneModel = Relationship()
    # 使用字符串引用避免循环导入
    morphology: "MorphologyModel" | None = Relationship()
    pet: "PetModel" | None = Relationship(back_populates="extra_gene_list")
