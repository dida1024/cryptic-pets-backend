from typing import TYPE_CHECKING

from sqlalchemy import JSON, Column, ForeignKey, String
from sqlmodel import Enum, Field, Relationship

from domain.pet_records.pet_record_data import PetRecordData
from domain.pet_records.value_objects import PetEventTypeEnum
from infrastructure.persistence.postgres.models.base import BaseModel

if TYPE_CHECKING:
    from infrastructure.persistence.postgres.models.pet import PetModel
    from infrastructure.persistence.postgres.models.user import UserModel


class PetRecordModel(BaseModel, table=True):
    """Pet record model representing a pet record in the database."""

    __tablename__ = "pet_records"

    pet_id: str = Field(
        sa_column=Column(String, ForeignKey("pets.id"), nullable=False),
        description="ID of the pet"
    )

    creator_id: str = Field(
        sa_column=Column(String, ForeignKey("users.id"), nullable=False),
        description="ID of the creator"
    )

    event_type: PetEventTypeEnum = Field(
        sa_column=Column(Enum(PetEventTypeEnum), nullable=False),
    )
    event_data: PetRecordData = Field(
        sa_column=Column(JSON, nullable=False),
        description="Data of the record"
    )

    pet: "PetModel" = Relationship()
    creator: "UserModel" = Relationship()
