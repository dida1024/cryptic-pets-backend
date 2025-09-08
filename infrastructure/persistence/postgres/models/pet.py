from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlmodel import Field, Relationship

from domain.pets.value_objects import GenderEnum
from infrastructure.persistence.postgres.models.base import BaseModel
from infrastructure.persistence.postgres.models.breed import BreedModel
from infrastructure.persistence.postgres.models.morphology import MorphologyModel

if TYPE_CHECKING:
    from infrastructure.persistence.postgres.models.morph_gene_mapping import (
        MorphGeneMappingModel,
    )
    from infrastructure.persistence.postgres.models.user import UserModel


class PetModel(BaseModel, table=True):
    """Pets model representing a pet in the database."""

    __tablename__ = "pets"

    name: str = Field(
        sa_column=Column(String, nullable=False),
        description="Name of the pet",
    )
    description: str | None = Field(
        sa_column=Column(String, nullable=True),
        description="Description of the pet",
    )
    birth_date: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True),
        description="Birth date of the pet",
    )
    owner_id: str = Field(
        sa_column=Column(String, ForeignKey("users.id"), nullable=False),
        description="Foreign key to owner"
    )
    breed_id: str = Field(
        sa_column=Column(String, ForeignKey("breeds.id"), nullable=False),
        description="Foreign key to breed",
    )
    gender: GenderEnum = Field(
        sa_column=Column(Enum(GenderEnum), nullable=False, default=GenderEnum.UNKNOWN),
        description="Gender of the pet",
    )
    morphology_id: str | None = Field(
        sa_column=Column(String, ForeignKey("morphologies.id"), nullable=True),
        description="Foreign key to morphology",
    )

    # Relationships
    breed: BreedModel = Relationship()
    morphology: MorphologyModel | None = Relationship()
    owner: "UserModel" = Relationship(back_populates="pets")
    # 使用字符串引用避免循环导入
    extra_gene_list: list["MorphGeneMappingModel"] = Relationship(back_populates="pet")
