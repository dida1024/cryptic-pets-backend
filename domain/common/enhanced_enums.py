"""Enhanced enum value objects with validation and business rules."""

from enum import Enum
from typing import Any

from pydantic import Field, field_validator

from domain.common.value_object_base import ValueObject


class EnhancedEnum(ValueObject):
    """Base class for enhanced enum value objects."""

    value: str = Field(..., description="Enum value")

    @field_validator('value')
    @classmethod
    def validate_value(cls, v: str) -> str:
        """Validate enum value."""
        if not v or not v.strip():
            raise ValueError("Enum value cannot be empty")
        return v.strip()

    def __str__(self) -> str:
        """String representation."""
        return self.value

    def __eq__(self, other: Any) -> bool:
        """Compare with other enum values."""
        if isinstance(other, str):
            return self.value == other
        if isinstance(other, self.__class__):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        """Hash based on value."""
        return hash(self.value)


class Gender(EnhancedEnum):
    """Gender value object with validation."""

    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"

    @field_validator('value')
    @classmethod
    def validate_gender(cls, v: str) -> str:
        """Validate gender value."""
        valid_genders = {cls.MALE, cls.FEMALE, cls.UNKNOWN}
        if v not in valid_genders:
            raise ValueError(f"Invalid gender: {v}. Must be one of {valid_genders}")
        return v

    @classmethod
    def male(cls) -> "Gender":
        """Create male gender."""
        return cls(value=cls.MALE)

    @classmethod
    def female(cls) -> "Gender":
        """Create female gender."""
        return cls(value=cls.FEMALE)

    @classmethod
    def unknown(cls) -> "Gender":
        """Create unknown gender."""
        return cls(value=cls.UNKNOWN)

    def is_male(self) -> bool:
        """Check if gender is male."""
        return self.value == self.MALE

    def is_female(self) -> bool:
        """Check if gender is female."""
        return self.value == self.FEMALE

    def is_unknown(self) -> bool:
        """Check if gender is unknown."""
        return self.value == self.UNKNOWN


class PetType(EnhancedEnum):
    """Pet type value object with validation."""

    DOG = "dog"
    CAT = "cat"
    OTHER = "other"

    @field_validator('value')
    @classmethod
    def validate_pet_type(cls, v: str) -> str:
        """Validate pet type value."""
        valid_types = {cls.DOG, cls.CAT, cls.OTHER}
        if v not in valid_types:
            raise ValueError(f"Invalid pet type: {v}. Must be one of {valid_types}")
        return v

    @classmethod
    def dog(cls) -> "PetType":
        """Create dog pet type."""
        return cls(value=cls.DOG)

    @classmethod
    def cat(cls) -> "PetType":
        """Create cat pet type."""
        return cls(value=cls.CAT)

    @classmethod
    def other(cls) -> "PetType":
        """Create other pet type."""
        return cls(value=cls.OTHER)

    def is_dog(self) -> bool:
        """Check if pet type is dog."""
        return self.value == self.DOG

    def is_cat(self) -> bool:
        """Check if pet type is cat."""
        return self.value == self.CAT

    def is_other(self) -> bool:
        """Check if pet type is other."""
        return self.value == self.OTHER


class InheritanceType(EnhancedEnum):
    """Inheritance type value object with validation."""

    DOMINANT = "dominant"
    RECESSIVE = "recessive"
    X_LINKED = "x_linked"
    Y_LINKED = "y_linked"
    AUTOSOMAL_DOMINANT = "autosomal_dominant"
    AUTOSOMAL_RECESSIVE = "autosomal_recessive"
    OTHER = "other"

    @field_validator('value')
    @classmethod
    def validate_inheritance_type(cls, v: str) -> str:
        """Validate inheritance type value."""
        valid_types = {
            cls.DOMINANT, cls.RECESSIVE, cls.X_LINKED, cls.Y_LINKED,
            cls.AUTOSOMAL_DOMINANT, cls.AUTOSOMAL_RECESSIVE, cls.OTHER
        }
        if v not in valid_types:
            raise ValueError(f"Invalid inheritance type: {v}. Must be one of {valid_types}")
        return v

    def is_dominant(self) -> bool:
        """Check if inheritance type is dominant."""
        return self.value in {self.DOMINANT, self.AUTOSOMAL_DOMINANT}

    def is_recessive(self) -> bool:
        """Check if inheritance type is recessive."""
        return self.value in {self.RECESSIVE, self.AUTOSOMAL_RECESSIVE}

    def is_sex_linked(self) -> bool:
        """Check if inheritance type is sex-linked."""
        return self.value in {self.X_LINKED, self.Y_LINKED}

    def is_autosomal(self) -> bool:
        """Check if inheritance type is autosomal."""
        return self.value in {self.AUTOSOMAL_DOMINANT, self.AUTOSOMAL_RECESSIVE}


class GeneCategory(EnhancedEnum):
    """Gene category value object with validation."""

    COLOR = "color"
    PATTERN = "pattern"
    TEXTURE = "texture"
    OTHER = "other"

    @field_validator('value')
    @classmethod
    def validate_gene_category(cls, v: str) -> str:
        """Validate gene category value."""
        valid_categories = {cls.COLOR, cls.PATTERN, cls.TEXTURE, cls.OTHER}
        if v not in valid_categories:
            raise ValueError(f"Invalid gene category: {v}. Must be one of {valid_categories}")
        return v

    def is_color(self) -> bool:
        """Check if gene category is color."""
        return self.value == self.COLOR

    def is_pattern(self) -> bool:
        """Check if gene category is pattern."""
        return self.value == self.PATTERN

    def is_texture(self) -> bool:
        """Check if gene category is texture."""
        return self.value == self.TEXTURE

    def is_other(self) -> bool:
        """Check if gene category is other."""
        return self.value == self.OTHER


class Zygosity(EnhancedEnum):
    """Zygosity value object with validation."""

    HOMOZYGOUS = "homozygous"
    HETEROZYGOUS = "heterozygous"
    UNKNOWN = "unknown"

    @field_validator('value')
    @classmethod
    def validate_zygosity(cls, v: str) -> str:
        """Validate zygosity value."""
        valid_zygosities = {cls.HOMOZYGOUS, cls.HETEROZYGOUS, cls.UNKNOWN}
        if v not in valid_zygosities:
            raise ValueError(f"Invalid zygosity: {v}. Must be one of {valid_zygosities}")
        return v

    def is_homozygous(self) -> bool:
        """Check if zygosity is homozygous."""
        return self.value == self.HOMOZYGOUS

    def is_heterozygous(self) -> bool:
        """Check if zygosity is heterozygous."""
        return self.value == self.HETEROZYGOUS

    def is_unknown(self) -> bool:
        """Check if zygosity is unknown."""
        return self.value == self.UNKNOWN


class UserType(EnhancedEnum):
    """User type value object with validation."""

    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

    @field_validator('value')
    @classmethod
    def validate_user_type(cls, v: str) -> str:
        """Validate user type value."""
        valid_types = {cls.ADMIN, cls.USER, cls.GUEST}
        if v not in valid_types:
            raise ValueError(f"Invalid user type: {v}. Must be one of {valid_types}")
        return v

    def is_admin(self) -> bool:
        """Check if user type is admin."""
        return self.value == self.ADMIN

    def is_user(self) -> bool:
        """Check if user type is user."""
        return self.value == self.USER

    def is_guest(self) -> bool:
        """Check if user type is guest."""
        return self.value == self.GUEST

    def has_admin_privileges(self) -> bool:
        """Check if user has admin privileges."""
        return self.value == self.ADMIN

    def can_modify_pets(self) -> bool:
        """Check if user can modify pets."""
        return self.value in {self.ADMIN, self.USER}
