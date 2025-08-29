
from datetime import datetime

from pydantic import BaseModel
from domain.pets.value_objects import GenderEnum


class CreatePetCommand(BaseModel):
    """创建宠物命令"""
    name: str
    owner_id: str
    breed_id: str
    description: str | None = None
    birth_date: datetime | None = None
    gender: GenderEnum = GenderEnum.UNKNOWN
    description: str | None = None


class UpdatePetCommand(BaseModel):
    """更新宠物命令"""
    pet_id: str
    name: str | None = None
    owner_id: str | None = None
    # 兼容字段（旧）
    age: int | None = None
    breed: str | None = None
    # 新字段
    breed_id: str | None = None
    birth_date: datetime | None = None
    gender: GenderEnum | None = None


class DeletePetCommand(BaseModel):
    """删除宠物命令"""
    pet_id: str


class ListPetsQuery(BaseModel):
    """宠物列表查询"""
    page: int = 1
    page_size: int = 10
    search: str | None = None
    owner_id: str | None = None
