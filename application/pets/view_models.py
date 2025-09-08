"""
宠物视图模型
为CQRS模式的查询结果提供专用的视图模型
"""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field, ConfigDict

from domain.common.entities import I18n
from domain.pets.value_objects import GenderEnum


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应基类"""
    
    items: list[T]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    
    @classmethod
    def create(cls, items: list[T], total: int, page: int, page_size: int) -> "PaginatedResponse[T]":
        """创建分页响应"""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            items=items,
            total_count=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


class OwnerView(BaseModel):
    """宠物主人视图模型"""
    
    id: str
    username: str
    full_name: str | None = None
    
    model_config = ConfigDict(from_attributes=True)


class BreedView(BaseModel):
    """品种视图模型"""
    
    id: str
    name: dict[str, str] | None = None  # I18n转换为字典
    description: dict[str, str] | None = None  # I18n转换为字典
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_entity(cls, breed: Any, language: str = "en") -> "BreedView":
        """从实体创建视图模型"""
        if not breed:
            return None
            
        return cls(
            id=breed.id,
            name=breed.name.dict() if isinstance(breed.name, I18n) else breed.name,
            description=breed.description.dict() if breed.description and isinstance(breed.description, I18n) else breed.description,
        )


class MorphologyView(BaseModel):
    """形态学视图模型"""
    
    id: str
    name: dict[str, str] | None = None  # I18n转换为字典
    description: dict[str, str] | None = None  # I18n转换为字典
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_entity(cls, morphology: Any, language: str = "en") -> "MorphologyView":
        """从实体创建视图模型"""
        if not morphology:
            return None
            
        return cls(
            id=morphology.id,
            name=morphology.name.dict() if isinstance(morphology.name, I18n) else morphology.name,
            description=morphology.description.dict() if morphology.description and isinstance(morphology.description, I18n) else morphology.description,
        )


class PictureView(BaseModel):
    """图片视图模型"""
    
    url: str
    title: str | None = None
    description: str | None = None
    is_primary: bool = False
    
    model_config = ConfigDict(from_attributes=True)


class PetSummaryView(BaseModel):
    """宠物摘要视图模型 - 用于列表展示"""
    
    id: str
    name: str
    gender: GenderEnum
    created_at: datetime
    owner_name: str | None = None
    breed_name: str | None = None
    primary_picture_url: str | None = None
    
    model_config = ConfigDict(from_attributes=True)


class PetDetailsView(BaseModel):
    """宠物详情视图模型 - 用于详情页展示"""
    
    id: str
    name: str
    description: str | None = None
    birth_date: datetime | None = None
    gender: GenderEnum
    created_at: datetime
    updated_at: datetime
    owner: OwnerView | None = None
    breed: BreedView | None = None
    morphology: MorphologyView | None = None
    pictures: list[PictureView] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)


class PetSearchResult(BaseModel):
    """宠物搜索结果"""
    
    pets: list[PetSummaryView]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    
    @classmethod
    def create(cls, pets: list[PetSummaryView], total: int, page: int, page_size: int) -> "PetSearchResult":
        """创建搜索结果"""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            pets=pets,
            total_count=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
