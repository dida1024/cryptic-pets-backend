from domain.pet_records.entities import PetRecord
from domain.pet_records.pet_record_data import PetRecordDataFactory
from infrastructure.persistence.postgres.mappers.base import BaseMapper
from infrastructure.persistence.postgres.models.pet_record import PetRecordModel


class PetRecordMapper(BaseMapper[PetRecord, PetRecordModel]):
    """宠物事件记录实体与模型转换器"""

    def to_domain(self, model: PetRecordModel) -> PetRecord:
        """数据库模型转换为领域实体"""
        # 解析事件数据
        event_data = PetRecordDataFactory.parse_data(
            event_type=model.event_type,
            data=model.event_data
        )

        return PetRecord(
            id=model.id,
            pet_id=model.pet_id,
            creator_id=model.creator_id,
            event_type=model.event_type,
            event_data=event_data,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_deleted=model.is_deleted,
        )

    def to_model(self, entity: PetRecord) -> PetRecordModel:
        """领域实体转换为数据库模型"""
        return PetRecordModel(
            id=entity.id,
            pet_id=entity.pet_id,
            creator_id=entity.creator_id,
            event_type=entity.event_type,
            event_data=entity.event_data.model_dump(),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_deleted=entity.is_deleted,
        )
