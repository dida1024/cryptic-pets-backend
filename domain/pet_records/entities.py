from pydantic import Field

from domain.common.aggregate_root import AggregateRoot
from domain.pet_records.pet_record_data import PetRecordData
from domain.pet_records.value_objects import PetEventTypeEnum


class PetRecord(AggregateRoot):
    """Pet record entity representing a pet record in the system."""

    pet_id: str = Field(..., description="ID of the pet")
    creator_id: str = Field(..., description="ID of the creator")
    event_type: PetEventTypeEnum = Field(..., description="Type of the record")
    event_data: PetRecordData = Field(..., description="Data of the record")
