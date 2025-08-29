

from datetime import datetime

from pydantic import BaseModel, Field

from domain.pets.entities import Breed
from domain.pets.value_objects import GenderEnum
from interfaces.http.v1.schemas.user_schemas import UserBaseSchema


class BreedBaseSchema(Breed):
    """宠物品种基础架构"""
    pass

class PetBaseSchema(BaseModel):
    """宠物基础架构"""
    name: str = Field(..., min_length=3, max_length=50, description="宠物名称")
    owner: UserBaseSchema = Field(..., description="宠物主人")
    breed: BreedBaseSchema = Field(..., description="宠物品种")
    description: str | None = Field(None, max_length=100, description="宠物描述")
    is_active: bool = Field(default=True, description="是否激活")

class PetResponse(PetBaseSchema):
    """宠物响应"""
    id: str = Field(..., description="宠物ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    is_deleted: bool = Field(..., description="是否删除")

class CreatePetRequest(BaseModel):
    """创建宠物请求"""
    name: str = Field(..., min_length=3, max_length=50, description="宠物名称")
    breed_id: str = Field(..., description="宠物品种ID")
    birth_date: datetime | None = Field(None, description="宠物出生日期")
    gender: GenderEnum = Field(default=GenderEnum.UNKNOWN, description="宠物性别")
    description: str | None = Field(None, max_length=100, description="宠物描述")

class UpdatePetRequest(BaseModel):
    """更新宠物请求"""
    name: str | None = Field(None, min_length=3, max_length=50, description="宠物名称")
    breed_id: str | None = Field(None, description="宠物品种ID")
    birth_date: datetime | None = Field(None, description="宠物出生日期")
    gender: GenderEnum | None = Field(None, description="宠物性别")
    description: str | None = Field(None, max_length=100, description="宠物描述")
    is_active: bool | None = Field(None, description="是否激活")
