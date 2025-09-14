"""
品种查询模型
实现CQRS模式的查询部分
"""

from pydantic import BaseModel, Field


class GetBreedByIdQuery(BaseModel):
    """根据ID获取品种查询"""
    breed_id: str
    include_pets: bool = Field(default=False, description="是否包含该品种的宠物信息")


class GetBreedByNameQuery(BaseModel):
    """根据名称获取品种查询"""
    name: str
    language: str = Field(default="en", description="搜索使用的语言")
    include_pets: bool = Field(default=False, description="是否包含该品种的宠物信息")


class SearchBreedsQuery(BaseModel):
    """搜索品种查询"""
    search_term: str | None = Field(default=None, description="搜索关键词")
    language: str = Field(default="en", description="搜索使用的语言")
    page: int = Field(default=1, description="页码，从1开始")
    page_size: int = Field(default=10, description="每页大小")
    include_deleted: bool = Field(default=False, description="是否包含已删除的品种")


class ListBreedsQuery(BaseModel):
    """品种列表查询（保持向后兼容）"""
    page: int = Field(default=1, description="页码，从1开始")
    page_size: int = Field(default=10, description="每页大小")
    include_deleted: bool = Field(default=False, description="是否包含已删除的品种")
