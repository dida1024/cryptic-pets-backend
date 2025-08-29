from sqlalchemy import JSON, Column, Enum, String
from sqlmodel import Field

from domain.pets.value_objects import GeneCategoryEnum, InheritanceTypeEnum
from infrastructure.persistence.postgres.models.base import BaseModel


class GeneModel(BaseModel, table=True):
    """Gene model representing a gene in the database."""

    __tablename__ = "genes"

    name: dict[str, str] = Field(
        sa_column=Column(JSON, nullable=False),
        description="I18n name of the gene"
    )
    alias: dict[str, str] | None = Field(
        sa_column=Column(JSON, nullable=True),
        description="I18n alias of the gene"
    )
    description: dict[str, str] | None = Field(
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
