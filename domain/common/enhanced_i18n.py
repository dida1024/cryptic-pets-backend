"""Enhanced I18n value object with improved immutability and validation."""


from pydantic import Field, field_validator

from domain.common.value_object_base import ValueObject
from domain.common.value_objects import I18nEnum


class I18n(ValueObject):
    """Enhanced I18n value object with improved immutability and validation.

    This value object represents internationalized text content with support for
    multiple languages. It provides type safety, validation, and immutability.
    """

    content: dict[I18nEnum, str] = Field(
        default_factory=dict,
        description="Internationalized content mapping language codes to text"
    )

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: dict[I18nEnum, str]) -> dict[I18nEnum, str]:
        """Validate the content dictionary."""
        if not v:
            raise ValueError("I18n content cannot be empty")

        # Validate that all values are non-empty strings
        for lang, text in v.items():
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"Text for language {lang} cannot be empty")

        return v

    def get_text(self, language: I18nEnum | str, fallback_language: I18nEnum | str | None = None) -> str | None:
        """Get text for the specified language with optional fallback."""
        if not self.content:
            return None

        # Convert string to enum if needed
        lang_enum = self._to_enum(language)
        if lang_enum and lang_enum in self.content:
            return self.content[lang_enum]

        # Try fallback language
        if fallback_language:
            fallback_enum = self._to_enum(fallback_language)
            if fallback_enum and fallback_enum in self.content:
                return self.content[fallback_enum]

        return None

    def with_text(self, language: I18nEnum | str, text: str) -> "I18n":
        """Create a new I18n instance with updated text for the specified language."""
        if not text.strip():
            raise ValueError("Text cannot be empty")

        lang_enum = self._to_enum(language)
        updated_content = dict(self.content)
        updated_content[lang_enum] = text.strip()

        return I18n(content=updated_content)

    def without_language(self, language: I18nEnum | str) -> "I18n":
        """Create a new I18n instance without the specified language."""
        lang_enum = self._to_enum(language)
        updated_content = dict(self.content)
        updated_content.pop(lang_enum, None)

        if not updated_content:
            raise ValueError("Cannot remove the last language from I18n")

        return I18n(content=updated_content)

    def has_language(self, language: I18nEnum | str) -> bool:
        """Check if the I18n instance has text for the specified language."""
        lang_enum = self._to_enum(language)
        return lang_enum in self.content

    def get_available_languages(self) -> list[I18nEnum]:
        """Get list of available languages."""
        return list(self.content.keys())

    def get_primary_text(self) -> str | None:
        """Get the primary text (first available language)."""
        if not self.content:
            return None
        return next(iter(self.content.values()))

    def is_complete(self, required_languages: list[I18nEnum] | None = None) -> bool:
        """Check if the I18n instance has text for all required languages."""
        if required_languages is None:
            required_languages = list(I18nEnum)

        return all(lang in self.content for lang in required_languages)

    def _to_enum(self, language: I18nEnum | str) -> I18nEnum:
        """Convert string to I18nEnum."""
        if isinstance(language, I18nEnum):
            return language
        try:
            return I18nEnum(language)
        except ValueError as e:
            raise ValueError(f"Invalid language code: {language}") from e

    def model_dump(self, *args, **kwargs) -> dict[str, str]:
        """Serialize to a plain dictionary with string keys."""
        result: dict[str, str] = {}
        for lang, text in self.content.items():
            result[lang.value] = text
        return result

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "I18n":
        """Create I18n instance from a dictionary with string keys."""
        content: dict[I18nEnum, str] = {}
        for lang_str, text in data.items():
            try:
                lang_enum = I18nEnum(lang_str)
                content[lang_enum] = text
            except ValueError:
                raise ValueError(f"Invalid language code: {lang_str}")

        return cls(content=content)

    @classmethod
    def create_single_language(cls, language: I18nEnum | str, text: str) -> "I18n":
        """Create I18n instance with text for a single language."""
        if not text.strip():
            raise ValueError("Text cannot be empty")

        lang_enum = cls._to_enum(language)
        return cls(content={lang_enum: text.strip()})

    @classmethod
    def create_bilingual(cls, zh_text: str, en_text: str) -> "I18n":
        """Create I18n instance with both Chinese and English text."""
        if not zh_text.strip() or not en_text.strip():
            raise ValueError("Both Chinese and English text must be provided")

        return cls(content={
            I18nEnum.ZH_CN: zh_text.strip(),
            I18nEnum.EN_US: en_text.strip()
        })

    def __str__(self) -> str:
        """String representation showing primary text."""
        primary = self.get_primary_text()
        return primary if primary else "I18n(empty)"

    def __len__(self) -> int:
        """Return the number of languages."""
        return len(self.content)
