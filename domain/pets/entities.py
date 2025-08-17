from datetime import datetime

from pydantic import Field

from domain.base_entity import BaseEntity
from domain.common.entities import I18nText, Picture
from domain.pets.value_objects import (
    GenderEnum,
    GeneCategoryEnum,
    InheritanceTypeEnum,
    ZygosityEnum,
)
from domain.users.entities import User


class Breed(BaseEntity):
    """Breed entity representing a breed in the system."""

    name: I18nText = Field(..., description="Name of the breed")
    description: I18nText | None = Field(default=None, description="Description of the breed")
    picture_list: list[Picture | None] = Field(default=[], description="List of pictures")

class Gene(BaseEntity):
    """Gene entity representing a gene in the system."""

    name: I18nText = Field(..., description="Name of the gene")
    alias: I18nText | None = Field(default=None, description="Alias of the gene")
    description: I18nText | None = Field(default=None, description="Description of the gene")
    notation: str | None = Field(default=None, description="Notation of the gene")
    inheritance_type: InheritanceTypeEnum | None = Field(default=None, description="Inheritance type of the gene")
    category: GeneCategoryEnum | None = Field(default=None, description="Category of the gene")
    picture_list: list[Picture | None] = Field(default=[], description="List of pictures")


class MorphGeneMapping(BaseEntity):
    gene: Gene = Field(..., description="The gene in this morphology/pet")
    zygosity: ZygosityEnum = Field(default=ZygosityEnum.UNKNOWN, description="homozygous / heterozygous / unknown")
    is_required: bool = Field(default=True, description="Is this gene required for the morphology expression")

class Morphology(BaseEntity):
    """Morphology entity representing a morphology in the system."""

    name: I18nText = Field(..., description="Name of the morphology")
    description: I18nText | None = Field(default=None, description="Description of the morphology")
    gene_mappings: list[MorphGeneMapping | None] = Field(default=[], description="List of genes")
    picture_list: list[Picture | None] = Field(default=[], description="List of pictures")


class Pets(BaseEntity):
    """Pets entity representing a pet in the system."""

    name: I18nText = Field(..., description="Name of the pet")
    birth_date: datetime | None = Field(None, description="Birth date of the pet")
    owner: User = Field(..., description="Owner of the pet")
    breed: Breed = Field(..., description="Breed of the pet")
    gender: GenderEnum = Field(default=GenderEnum.UNKNOWN, description="Gender of the pet")
    extra_gene_list: list[MorphGeneMapping | None] = Field(default=[], description="List of extra genes")
    morphology: Morphology | None = Field(None, description="Morphology of the pet")
    picture_list: list[Picture | None] = Field(default=[], description="List of pictures")
