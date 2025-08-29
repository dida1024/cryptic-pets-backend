from datetime import datetime

from pydantic import BaseModel, Field

from domain.common.entities import I18n


class BreedBaseSchema(BaseModel):
    """品种基础模型（i18n采用扁平 dict）"""
    name: I18n = Field(..., description="品种名称（i18n）")
    description: I18n | None = Field(None, description="品种描述（i18n）")


class BreedResponse(BreedBaseSchema):
    id: str = Field(..., description="品种ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    is_deleted: bool = Field(..., description="是否删除")


class CreateBreedRequest(BreedBaseSchema):
    pass


class UpdateBreedRequest(BaseModel):
    name: I18n | None = Field(None, description="品种名称（i18n）")
    description: I18n | None = Field(None, description="品种描述（i18n）")


