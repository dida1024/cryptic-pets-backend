from sqlalchemy import Column, Enum, String
from sqlmodel import Field

from domain.common.value_objects import EntityTypeEnum, PictureEnum
from infrastructure.persistence.postgres.models.base import BaseModel


class Picture(BaseModel, table=True):
    """Picture model representing a picture in the database."""

    __tablename__ = "pictures"

    picture_url: str = Field(
        sa_column=Column(String, nullable=False),
        description="URL of the picture"
    )
    picture_type: PictureEnum = Field(
        sa_column=Column(Enum(PictureEnum), nullable=False),
        description="Type of the picture"
    )
    entity_id: str = Field(
        sa_column=Column(String, nullable=False),
        description="ID of the entity this picture belongs to"
    )
    entity_type: EntityTypeEnum = Field(
        sa_column=Column(Enum(EntityTypeEnum), nullable=False),
        description="Type of the entity"
    )
