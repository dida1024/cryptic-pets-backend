"""
宠物记录视图模型
用于CQRS模式的查询响应
"""

from datetime import datetime

from pydantic import BaseModel, SerializeAsAny

from domain.pet_records.entities import PetRecord
from domain.pet_records.pet_record_data import PetRecordData
from domain.pet_records.value_objects import PetEventTypeEnum


class PetRecordSummaryView(BaseModel):
    """宠物记录摘要视图"""
    id: str
    pet_id: str
    creator_id: str
    event_type: PetEventTypeEnum
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, pet_record: PetRecord) -> "PetRecordSummaryView":
        """从宠物记录实体创建摘要视图"""
        return cls(
            id=pet_record.id,
            pet_id=pet_record.pet_id,
            creator_id=pet_record.creator_id,
            event_type=pet_record.event_type,
            created_at=pet_record.created_at,
            updated_at=pet_record.updated_at,
        )


class PetRecordDetailsView(BaseModel):
    """宠物记录详情视图"""
    id: str
    pet_id: str
    creator_id: str
    event_type: PetEventTypeEnum
    event_data: SerializeAsAny[PetRecordData]
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    @classmethod
    def from_entity(cls, pet_record: PetRecord) -> "PetRecordDetailsView":
        """从宠物记录实体创建详情视图"""
        return cls(
            id=pet_record.id,
            pet_id=pet_record.pet_id,
            creator_id=pet_record.creator_id,
            event_type=pet_record.event_type,
            event_data=pet_record.event_data,
            created_at=pet_record.created_at,
            updated_at=pet_record.updated_at,
            is_deleted=pet_record.is_deleted,
        )


class PetRecordSearchResult(BaseModel):
    """宠物记录搜索结果"""
    records: list[PetRecordSummaryView]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(
        cls,
        records: list[PetRecordSummaryView],
        total: int,
        page: int,
        page_size: int,
    ) -> "PetRecordSearchResult":
        """创建搜索结果"""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            records=records,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
