

from datetime import datetime

from pydantic import BaseModel, Field

from domain.common.entities import I18n
from domain.pets.value_objects import GenderEnum
from interfaces.http.v1.schemas.user_schemas import UserBaseSchema


class BreedBaseSchema(BaseModel):
    """宠物品种基础架构"""
    id: str = Field(..., description="品种ID")
    name: dict = Field(..., description="品种名称（多语言）")
    description: dict | None = Field(None, description="品种描述（多语言）")

class PetBaseSchema(BaseModel):
    """宠物基础架构"""
    name: str = Field(..., min_length=3, max_length=50, description="宠物名称")
    owner_id: str = Field(..., description="宠物主人ID")
    breed_id: str = Field(..., description="宠物品种ID")
    description: str | None = Field(None, max_length=100, description="宠物描述")
    gender: GenderEnum = Field(default=GenderEnum.UNKNOWN, description="宠物性别")
    birth_date: datetime | None = Field(None, description="宠物出生日期")
    morphology_id: str | None = Field(None, description="宠物品系ID")

class PetResponse(PetBaseSchema):
    """宠物响应"""
    id: str = Field(..., description="宠物ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    is_deleted: bool = Field(..., description="是否删除")

class CreatePetRequest(BaseModel):
    """创建宠物请求"""
    name: str = Field(..., min_length=3, max_length=50, description="宠物名称")
    owner_id: str = Field(..., description="宠物主人ID")
    breed_id: str = Field(..., description="宠物品种ID")
    birth_date: datetime | None = Field(None, description="宠物出生日期")
    gender: GenderEnum = Field(default=GenderEnum.UNKNOWN, description="宠物性别")
    description: str | None = Field(None, max_length=100, description="宠物描述")
    morphology_id: str | None = Field(None, description="宠物品系ID")
    extra_gene_list: list | None = Field(None, description="额外基因列表")

class UpdatePetRequest(BaseModel):
    """更新宠物请求"""
    name: str | None = Field(None, min_length=3, max_length=50, description="宠物名称")
    owner_id: str | None = Field(None, description="宠物主人ID")
    breed_id: str | None = Field(None, description="宠物品种ID")
    birth_date: datetime | None = Field(None, description="宠物出生日期")
    gender: GenderEnum | None = Field(None, description="宠物性别")
    description: str | None = Field(None, max_length=100, description="宠物描述")
    morphology_id: str | None = Field(None, description="宠物品系ID")


class TransferPetOwnershipRequest(BaseModel):
    """转移宠物所有权请求"""
    new_owner_id: str = Field(..., description="新主人ID")
    current_user_id: str = Field(..., description="当前用户ID")


class PetDetailResponse(PetResponse):
    """宠物详情响应"""
    owner: UserBaseSchema | None = Field(None, description="宠物主人")
    breed: BreedBaseSchema | None = Field(None, description="宠物品种")


class PetSummaryResponse(BaseModel):
    """宠物摘要响应"""
    id: str = Field(..., description="宠物ID")
    name: str = Field(..., description="宠物名称")
    gender: GenderEnum = Field(..., description="宠物性别")
    created_at: datetime = Field(..., description="创建时间")
    owner_name: str | None = Field(None, description="主人名称")
    breed_name: I18n | None = Field(None, description="品种名称")
    primary_picture_url: str | None = Field(None, description="主图URL")
