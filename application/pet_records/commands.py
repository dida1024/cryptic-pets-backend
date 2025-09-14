from pydantic import BaseModel, Field

from domain.pet_records.value_objects import PetEventTypeEnum


class CreatePetRecordCommand(BaseModel):
    """创建宠物事件记录命令"""
    pet_id: str = Field(..., description="宠物ID")
    creator_id: str = Field(..., description="创建者ID")
    event_type: PetEventTypeEnum = Field(..., description="事件类型")
    event_data: dict = Field(..., description="事件数据")


class UpdatePetRecordCommand(BaseModel):
    """更新宠物事件记录命令"""
    record_id: str = Field(..., description="记录ID")
    event_data: dict | None = Field(None, description="事件数据")


class DeletePetRecordCommand(BaseModel):
    """删除宠物事件记录命令"""
    record_id: str = Field(..., description="记录ID")


# 特定事件类型的命令类
class CreateFeedingRecordCommand(BaseModel):
    """创建喂食记录命令"""
    pet_id: str = Field(..., description="宠物ID")
    creator_id: str = Field(..., description="创建者ID")
    food_name: str = Field(..., description="食物名称")
    food_amount: float = Field(..., description="喂食数量")
    food_unit: str | None = Field("g", description="喂食单位，默认克")
    feeding_method: str | None = Field(None, description="喂食方式")
    description: str | None = Field(None, description="详细备注或说明")
    notes: str | None = Field(None, description="其他备注")


class CreateWeighingRecordCommand(BaseModel):
    """创建称重记录命令"""
    pet_id: str = Field(..., description="宠物ID")
    creator_id: str = Field(..., description="创建者ID")
    weight: float = Field(..., description="体重数值")
    weight_unit: str | None = Field("g", description="体重单位，默认克")
    scale_type: str | None = Field(None, description="称重工具类型或型号")
    condition: str | None = Field(None, description="称重时宠物状态")
    description: str | None = Field(None, description="备注信息")
    notes: str | None = Field(None, description="其他备注")


class CreateSheddingRecordCommand(BaseModel):
    """创建蜕皮记录命令"""
    pet_id: str = Field(..., description="宠物ID")
    creator_id: str = Field(..., description="创建者ID")
    shedding_area: str | None = Field(None, description="蜕皮部位")
    shedding_degree: str | None = Field(None, description="蜕皮程度")
    shedding_type: str | None = Field(None, description="蜕皮类型")
    description: str | None = Field(None, description="其他备注")
    notes: str | None = Field(None, description="其他备注")


class CreateHealthRecordCommand(BaseModel):
    """创建健康记录命令"""
    pet_id: str = Field(..., description="宠物ID")
    creator_id: str = Field(..., description="创建者ID")
    symptom: str | None = Field(None, description="症状描述")
    severity: str | None = Field(None, description="严重程度")
    treatment: str | None = Field(None, description="治疗方式")
    vet_visit: bool | None = Field(None, description="是否去过兽医")
    description: str | None = Field(None, description="其他备注")
    notes: str | None = Field(None, description="其他备注")


class CreateBehaviorRecordCommand(BaseModel):
    """创建行为记录命令"""
    pet_id: str = Field(..., description="宠物ID")
    creator_id: str = Field(..., description="创建者ID")
    behavior_type: str | None = Field(None, description="行为类型")
    duration_minutes: float | None = Field(None, description="持续时间（分钟）")
    intensity: str | None = Field(None, description="行为强度")
    description: str | None = Field(None, description="其他备注")
    notes: str | None = Field(None, description="其他备注")


class CreateEnvironmentalRecordCommand(BaseModel):
    """创建环境记录命令"""
    pet_id: str = Field(..., description="宠物ID")
    creator_id: str = Field(..., description="创建者ID")
    temperature: float | None = Field(None, description="温度")
    humidity: float | None = Field(None, description="湿度")
    light_condition: str | None = Field(None, description="光照情况")
    description: str | None = Field(None, description="其他备注")
    notes: str | None = Field(None, description="其他备注")


class CreateOtherRecordCommand(BaseModel):
    """创建其他记录命令"""
    pet_id: str = Field(..., description="宠物ID")
    creator_id: str = Field(..., description="创建者ID")
    description: str | None = Field(None, description="自定义记录描述")
    notes: str | None = Field(None, description="其他备注")


