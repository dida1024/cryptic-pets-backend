from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from domain.pet_records.pet_record_data import PetRecordDataFactory
from domain.pet_records.value_objects import PetEventTypeEnum


class PetRecordBaseSchema(BaseModel):
    """宠物记录基础模型"""
    pet_id: str = Field(..., description="宠物ID")
    creator_id: str = Field(..., description="创建者ID")
    event_type: PetEventTypeEnum = Field(..., description="事件类型")
    event_data: dict = Field(..., description="事件数据")

class PetRecordResponse(PetRecordBaseSchema):
    """宠物记录响应模型"""
    id: str = Field(..., description="记录ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    is_deleted: bool = Field(..., description="是否删除")


class PetRecordSummaryResponse(BaseModel):
    """宠物记录摘要响应模型（用于列表/搜索）"""
    id: str = Field(..., description="记录ID")
    pet_id: str = Field(..., description="宠物ID")
    creator_id: str = Field(..., description="创建者ID")
    event_type: PetEventTypeEnum = Field(..., description="事件类型")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class CreatePetRecordRequest(BaseModel):
    """创建宠物记录请求模型"""
    pet_id: str = Field(..., description="宠物ID")
    creator_id: str = Field(..., description="创建者ID")


class UpdatePetRecordRequest(BaseModel):
    """更新宠物记录请求模型"""
    event_data: dict | None = Field(None, description="事件数据")


class PetRecordSearchRequest(BaseModel):
    """宠物记录搜索请求模型"""
    search_term: str | None = Field(None, description="搜索关键词")
    pet_id: str | None = Field(None, description="宠物ID")
    event_type: PetEventTypeEnum | None = Field(None, description="事件类型")
    creator_id: str | None = Field(None, description="创建者ID")
    page: int = Field(default=1, description="页码，从1开始")
    page_size: int = Field(default=10, description="每页大小")
    include_deleted: bool = Field(default=False, description="是否包含已删除的记录")


class PetRecordListRequest(BaseModel):
    """宠物记录列表请求模型"""
    page: int = Field(default=1, description="页码，从1开始")
    page_size: int = Field(default=10, description="每页大小")
    search: str | None = Field(None, description="搜索关键词")
    pet_id: str | None = Field(None, description="宠物ID")
    event_type: PetEventTypeEnum | None = Field(None, description="事件类型")
    creator_id: str | None = Field(None, description="创建者ID")
    include_deleted: bool = Field(default=False, description="是否包含已删除的记录")


# 特定事件类型的请求模型
class CreateFeedingRecordRequest(CreatePetRecordRequest):
    """创建喂食记录请求模型"""
    food_name: str = Field(..., description="食物名称")
    food_amount: float = Field(..., description="喂食数量")
    food_unit: str | None = Field("g", description="喂食单位，默认克")
    feeding_method: str | None = Field(None, description="喂食方式")
    description: str | None = Field(None, description="详细备注或说明")
    notes: str | None = Field(None, description="其他备注")


class CreateWeighingRecordRequest(CreatePetRecordRequest):
    """创建称重记录请求模型"""
    weight: float = Field(..., description="体重数值")
    weight_unit: str | None = Field("g", description="体重单位，默认克")
    scale_type: str | None = Field(None, description="称重工具类型或型号")
    condition: str | None = Field(None, description="称重时宠物状态")
    description: str | None = Field(None, description="备注信息")
    notes: str | None = Field(None, description="其他备注")


class CreateSheddingRecordRequest(CreatePetRecordRequest):
    """创建蜕皮记录请求模型"""
    shedding_area: str | None = Field(None, description="蜕皮部位")
    shedding_degree: str | None = Field(None, description="蜕皮程度")
    shedding_type: str | None = Field(None, description="蜕皮类型")
    description: str | None = Field(None, description="其他备注")
    notes: str | None = Field(None, description="其他备注")


class CreateHealthRecordRequest(CreatePetRecordRequest):
    """创建健康记录请求模型"""
    symptom: str | None = Field(None, description="症状描述")
    severity: str | None = Field(None, description="严重程度")
    treatment: str | None = Field(None, description="治疗方式")
    vet_visit: bool | None = Field(None, description="是否去过兽医")
    description: str | None = Field(None, description="其他备注")
    notes: str | None = Field(None, description="其他备注")


class CreateBehaviorRecordRequest(CreatePetRecordRequest):
    """创建行为记录请求模型"""
    behavior_type: str | None = Field(None, description="行为类型")
    duration_minutes: float | None = Field(None, description="持续时间（分钟）")
    intensity: str | None = Field(None, description="行为强度")
    description: str | None = Field(None, description="其他备注")
    notes: str | None = Field(None, description="其他备注")


class CreateEnvironmentalRecordRequest(CreatePetRecordRequest):
    """创建环境记录请求模型"""
    temperature: float | None = Field(None, description="温度")
    humidity: float | None = Field(None, description="湿度")
    light_condition: str | None = Field(None, description="光照情况")
    description: str | None = Field(None, description="其他备注")
    notes: str | None = Field(None, description="其他备注")


class CreateOtherRecordRequest(CreatePetRecordRequest):
    """创建其他记录请求模型"""
    description: str | None = Field(None, description="自定义记录描述")
    notes: str | None = Field(None, description="其他备注")


