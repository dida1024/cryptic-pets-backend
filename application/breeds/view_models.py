"""
品种视图模型
用于CQRS模式的查询响应
"""

from datetime import datetime

from pydantic import BaseModel

from domain.common.entities import I18n
from domain.pets.entities import Breed


class BreedSummaryView(BaseModel):
    """品种摘要视图"""
    id: str
    name: I18n
    description: I18n | None = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    @classmethod
    def from_entity(cls, breed: Breed) -> "BreedSummaryView":
        """从品种实体创建摘要视图"""
        return cls(
            id=breed.id,
            name=breed.name,
            description=breed.description,
            created_at=breed.created_at,
            updated_at=breed.updated_at,
            is_deleted=breed.is_deleted,
        )


class BreedDetailsView(BaseModel):
    """品种详情视图"""
    id: str
    name: I18n
    description: I18n | None = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    # 可以添加更多详情信息

    @classmethod
    def from_entity(cls, breed: Breed) -> "BreedDetailsView":
        """从品种实体创建详情视图"""
        return cls(
            id=breed.id,
            name=breed.name,
            description=breed.description,
            created_at=breed.created_at,
            updated_at=breed.updated_at,
            is_deleted=breed.is_deleted,
        )


class BreedSearchResult(BaseModel):
    """品种搜索结果"""
    breeds: list[BreedSummaryView]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(
        cls,
        breeds: list[BreedSummaryView],
        total: int,
        page: int,
        page_size: int,
    ) -> "BreedSearchResult":
        """创建搜索结果"""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            breeds=breeds,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


class BreedWithPetsView(BaseModel):
    """包含宠物信息的品种视图"""
    breed: BreedDetailsView
    pets_count: int = 0
    # 可以添加宠物列表信息

    @classmethod
    def from_entity(cls, breed: Breed, pets_count: int = 0) -> "BreedWithPetsView":
        """从品种实体创建包含宠物信息的视图"""
        return cls(
            breed=BreedDetailsView.from_entity(breed),
            pets_count=pets_count,
        )
