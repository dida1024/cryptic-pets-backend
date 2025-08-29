from typing import TYPE_CHECKING

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship

from infrastructure.persistence.postgres.models.base import BaseModel

if TYPE_CHECKING:
    from infrastructure.persistence.postgres.models.morph_gene_mapping import (
        MorphGeneMappingModel,
    )


class MorphologyModel(BaseModel, table=True):
    """Morphology model representing a morphology in the database."""

    __tablename__ = "morphologies"

    name: dict[str, str] = Field(
        sa_column=Column(JSON, nullable=False),
        description="I18n name of the morphology"
    )
    description: dict[str, str] | None = Field(
        sa_column=Column(JSON, nullable=True),
        description="I18n description of the morphology"
    )

    # Relationships
    # 使用字符串引用避免循环导入
    gene_mappings: list["MorphGeneMappingModel"] = Relationship(
        back_populates="morphology"
    )
