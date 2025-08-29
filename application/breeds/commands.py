from pydantic import BaseModel

from domain.common.entities import I18n


class CreateBreedCommand(BaseModel):
    """创建品种命令"""
    name: I18n
    description: I18n | None = None


class UpdateBreedCommand(BaseModel):
    """更新品种命令"""
    breed_id: str
    name: I18n | None = None
    description: I18n | None = None


class DeleteBreedCommand(BaseModel):
    """删除品种命令"""
    breed_id: str


class ListBreedsQuery(BaseModel):
    """品种列表查询"""
    page: int = 1
    page_size: int = 10
    include_deleted: bool = False


class SearchBreedsQuery(BaseModel):
    """品种搜索查询"""
    search: str
    language: str = "en"
    page: int = 1
    page_size: int = 10
    include_deleted: bool = False


