"""
宠物查询模型
实现CQRS模式的查询部分
"""

from pydantic import BaseModel, Field


class GetPetByIdQuery(BaseModel):
    """根据ID获取宠物查询"""
    pet_id: str
    include_owner: bool = Field(default=False, description="是否包含主人信息")
    include_breed: bool = Field(default=False, description="是否包含品种信息")
    include_morphology: bool = Field(default=False, description="是否包含品系信息")


class GetPetByNameQuery(BaseModel):
    """根据名称获取宠物查询"""
    name: str
    language: str = Field(default="en", description="搜索使用的语言")


class SearchPetsQuery(BaseModel):
    """搜索宠物查询"""
    search_term: str | None = Field(default=None, description="搜索关键词")
    owner_id: str | None = Field(default=None, description="主人ID过滤")
    breed_id: str | None = Field(default=None, description="品种ID过滤")
    morphology_id: str | None = Field(default=None, description="品系ID过滤")
    gender: str | None = Field(default=None, description="性别过滤")
    page: int = Field(default=1, description="页码，从1开始")
    page_size: int = Field(default=10, description="每页大小")
    include_deleted: bool = Field(default=False, description="是否包含已删除的宠物")


class ListPetsByOwnerQuery(BaseModel):
    """列出用户的宠物查询"""
    owner_id: str
    page: int = Field(default=1, description="页码，从1开始")
    page_size: int = Field(default=10, description="每页大小")


class ListPetsByBreedQuery(BaseModel):
    """列出特定品种的宠物查询"""
    breed_id: str
    page: int = Field(default=1, description="页码，从1开始")
    page_size: int = Field(default=10, description="每页大小")


class ListPetsByMorphologyQuery(BaseModel):
    """列出特定品系的宠物查询"""
    morphology_id: str
    page: int = Field(default=1, description="页码，从1开始")
    page_size: int = Field(default=10, description="每页大小")
