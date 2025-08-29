
from pydantic import Field, RootModel

from domain.base_entity import BaseEntity
from domain.common.value_objects import EntityTypeEnum, I18nEnum, PictureEnum


class Picture(BaseEntity):
    """Picture entity representing a picture in the system."""

    picture_url: str = Field(..., description="URL of the picture")
    picture_type: PictureEnum = Field(..., description="Type of the picture")
    entity_id: str = Field(..., description="ID of the entity this picture belongs to")
    entity_type: EntityTypeEnum = Field(..., description="Type of the entity")

class I18n(RootModel[dict[I18nEnum, str]]):
    """I18n value object wrapping a mapping of locale -> text.

    - Keeps the domain model semantically clear (not just a raw dict)
    - Serializes to a plain JSON object in APIs (e.g., {"zh_CN": "名称"})
    - Provides small helpers for common operations
    """

    root: dict[I18nEnum, str]

    def get_text(self, language: I18nEnum | str, fallback_language: I18nEnum | str | None = None) -> str | None:
        """Return text for language, with optional fallback."""
        if not self.root:
            return None
        def to_enum(val: I18nEnum | str) -> I18nEnum | None:
            if isinstance(val, I18nEnum):
                return val
            try:
                return I18nEnum(val)
            except Exception:
                return None
        lang_enum = to_enum(language)
        if lang_enum and lang_enum in self.root:
            return self.root[lang_enum]
        if fallback_language:
            fb_enum = to_enum(fallback_language)
            if fb_enum and fb_enum in self.root:
                return self.root[fb_enum]
        return None

    def with_text(self, language: I18nEnum | str, value: str) -> "I18n":
        """Return a new I18n with the provided language updated."""
        updated: dict[I18nEnum, str] = dict(self.root or {})
        if isinstance(language, I18nEnum):
            lang_enum = language
        else:
            lang_enum = I18nEnum(language)
        updated[lang_enum] = value
        return I18n.model_validate(updated)

    # Ensure dumping/serialization produces a plain dict instead of {"root": {...}}
    def model_dump(self, *args, **kwargs) -> dict[str, str]:  # type: ignore[override]
        # Convert enum keys to their string values for JSON compat
        result: dict[str, str] = {}
        for k, v in (self.root or {}).items():
            key_str = k.value if isinstance(k, I18nEnum) else str(k)
            result[key_str] = v
        return result
