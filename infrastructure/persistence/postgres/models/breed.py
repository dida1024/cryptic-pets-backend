from sqlalchemy import JSON, Column
from sqlmodel import Field

from domain.common.entities import I18nText
from infrastructure.persistence.postgres.models.base import BaseModel


class BreedModel(BaseModel, table=True):
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
