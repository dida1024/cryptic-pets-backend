from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
)
from sqlmodel import Field, Relationship

from domain.common.entities import I18nText
from domain.pets.value_objects import (
    GenderEnum,
    GeneCategoryEnum,
    InheritanceTypeEnum,
    ZygosityEnum,
)
from infrastructure.persistence.postgres.models.base import BaseModel


class Breed(BaseModel, table=True):
    """Breed model representing a breed in the database."""

    __tablename__ = "breeds"

    name: I18nText = Field(
        sa_column=Column(JSON, nullable=False),
        description="I18n name of the breed"
    )
    description: I18nText | None = Field(
        sa_column=Column(JSON, nullable=True),
        description="I18n description of the breed"
    )


class Gene(BaseModel, table=True):
    """Gene model representing a gene in the database."""

    __tablename__ = "genes"

    name: I18nText = Field(
        sa_column=Column(JSON, nullable=False),
        description="I18n name of the gene"
    )
    alias: I18nText | None = Field(
        sa_column=Column(JSON, nullable=True),
        description="I18n alias of the gene"
    )
    description: I18nText | None = Field(
        sa_column=Column(JSON, nullable=True),
        description="I18n description of the gene"
    )
    notation: str | None = Field(
        sa_column=Column(String, nullable=True),
        description="Notation of the gene"
    )
    inheritance_type: InheritanceTypeEnum | None = Field(
        sa_column=Column(Enum(InheritanceTypeEnum), nullable=True),
        description="Inheritance type of the gene"
    )
    category: GeneCategoryEnum | None = Field(
        sa_column=Column(Enum(GeneCategoryEnum), nullable=True),
        description="Category of the gene"
    )


class Morphology(BaseModel, table=True):
    """Morphology model representing a morphology in the database."""

    __tablename__ = "morphologies"

    name: I18nText = Field(
        sa_column=Column(JSON, nullable=False),
        description="I18n name of the morphology"
    )
    description: I18nText | None = Field(
        sa_column=Column(JSON, nullable=True),
        description="I18n description of the morphology"
    )

    # Relationships
    gene_mappings: list["MorphGeneMapping"] = Relationship(
        back_populates="morphology",
        sa_relationship_kwargs={"foreign_keys": "MorphGeneMapping.morphology_id"}
    )


class Pets(BaseModel, table=True):
    """Pets model representing a pet in the database."""

    __tablename__ = "pets"

    name: I18nText = Field(
        sa_column=Column(JSON, nullable=False),
        description="I18n name of the pet"
    )
    birth_date: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True),
        description="Birth date of the pet"
    )
    owner_id: str = Field(
        sa_column=Column(String, ForeignKey("users.id"), nullable=False),
        description="Foreign key to owner"
    )
    breed_id: str = Field(
        sa_column=Column(String, ForeignKey("breeds.id"), nullable=False),
        description="Foreign key to breed"
    )
    gender: GenderEnum = Field(
        sa_column=Column(Enum(GenderEnum), nullable=False, default=GenderEnum.UNKNOWN),
        description="Gender of the pet"
    )
    morphology_id: str | None = Field(
        sa_column=Column(String, ForeignKey("morphologies.id"), nullable=True),
        description="Foreign key to morphology"
    )

    # Relationships
    breed: Breed = Relationship()
    morphology: Morphology | None = Relationship()
    extra_gene_list: list["MorphGeneMapping"] = Relationship(back_populates="pet")


class MorphGeneMapping(BaseModel, table=True):
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

    gene: Gene = Relationship()
    morphology: Morphology | None = Relationship()
    pet: Pets | None = Relationship(back_populates="extra_gene_list")
