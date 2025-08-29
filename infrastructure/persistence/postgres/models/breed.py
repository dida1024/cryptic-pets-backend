from sqlalchemy import JSON, Column
from sqlmodel import Field

from infrastructure.persistence.postgres.models.base import BaseModel


class BreedModel(BaseModel, table=True):
    """Breed model representing a breed in the database."""

    __tablename__ = "breeds"

    name: dict[str, str] = Field(
        sa_column=Column(JSON, nullable=False),
        description="I18n name of the breed keyed by locale"
    )
    description: dict[str, str] | None = Field(
        sa_column=Column(JSON, nullable=True),
        description="I18n description of the breed keyed by locale"
    )
