
from pydantic import Field

from domain.base_entity import BaseEntity
from domain.common.value_objects import EntityTypeEnum, I18nEnum, PictureEnum


class Picture(BaseEntity):
    """Picture entity representing a picture in the system."""

    picture_url: str = Field(..., description="URL of the picture")
    picture_type: PictureEnum = Field(..., description="Type of the picture")
    entity_id: str = Field(..., description="ID of the entity this picture belongs to")
    entity_type: EntityTypeEnum = Field(..., description="Type of the entity")

class I18nText(BaseEntity):
    """I18nText entity representing a i18n text in the system."""

    language: I18nEnum = Field(..., description="Language of the i18n text")
    value: str = Field(..., description="Value of the i18n")
