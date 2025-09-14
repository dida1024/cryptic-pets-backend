"""
宠物记录查询模型
实现CQRS模式的查询部分
"""

from pydantic import BaseModel, Field

from domain.pet_records.value_objects import PetEventTypeEnum


class GetPetRecordByIdQuery(BaseModel):
    """根据ID获取宠物记录查询"""
    pet_record_id: str = Field(..., description="宠物记录ID")


class SearchPetRecordsQuery(BaseModel):
    """搜索宠物记录查询"""
    search_term: str | None = Field(default=None, description="搜索关键词")
    pet_id: str | None = Field(default=None, description="宠物ID")
    event_type: PetEventTypeEnum | None = Field(default=None, description="事件类型")
    creator_id: str | None = Field(default=None, description="创建者ID")
    page: int = Field(default=1, description="页码，从1开始")
    page_size: int = Field(default=10, description="每页大小")
    include_deleted: bool = Field(default=False, description="是否包含已删除的记录")


class ListPetRecordsQuery(BaseModel):
    """宠物记录列表查询"""
    page: int = Field(default=1, description="页码，从1开始")
    page_size: int = Field(default=10, description="每页大小")
    search: str | None = Field(default=None, description="搜索关键词")
    pet_id: str | None = Field(default=None, description="宠物ID")
    event_type: PetEventTypeEnum | None = Field(default=None, description="事件类型")
    creator_id: str | None = Field(default=None, description="创建者ID")
    include_deleted: bool = Field(default=False, description="是否包含已删除的记录")
