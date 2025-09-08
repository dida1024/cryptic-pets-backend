from datetime import datetime

from pydantic import Field

from domain.base_entity import BaseEntity
from domain.common.entities import I18n, Picture
from domain.pets.value_objects import (
    GenderEnum,
    GeneCategoryEnum,
    InheritanceTypeEnum,
    ZygosityEnum,
)


class Breed(BaseEntity):
    """Breed entity representing a breed in the system."""

    name: I18n = Field(..., description="Name of the breed keyed by locale")
    description: I18n | None = Field(default=None, description="Description of the breed keyed by locale")
    picture_list: list[Picture | None] = Field(default=[], description="List of pictures")

class Gene(BaseEntity):
    """Gene entity representing a gene in the system."""

    name: I18n = Field(..., description="Name of the gene keyed by locale")
    alias: I18n | None = Field(default=None, description="Alias of the gene keyed by locale")
    description: I18n | None = Field(default=None, description="Description of the gene keyed by locale")
    notation: str | None = Field(default=None, description="Notation of the gene")
    inheritance_type: InheritanceTypeEnum | None = Field(default=None, description="Inheritance type of the gene")
    category: GeneCategoryEnum | None = Field(default=None, description="Category of the gene")
    picture_list: list[Picture | None] = Field(default=[], description="List of pictures")


class MorphGeneMapping(BaseEntity):
    gene_id: str = Field(..., description="ID of the gene in this morphology/pet")
    zygosity: ZygosityEnum = Field(default=ZygosityEnum.UNKNOWN, description="homozygous / heterozygous / unknown")
    is_required: bool = Field(default=True, description="Is this gene required for the morphology expression")

class Morphology(BaseEntity):
    """Morphology entity representing a morphology in the system."""

    name: I18n = Field(..., description="Name of the morphology keyed by locale")
    description: I18n | None = Field(default=None, description="Description of the morphology keyed by locale")
    gene_mapping_ids: list[str] = Field(default=[], description="List of gene mapping IDs")
    picture_list: list[Picture | None] = Field(default=[], description="List of pictures")


class Pet(BaseEntity):
    """Pet entity representing a pet in the system."""

    name: str = Field(..., description="Name of the pet")
    description: str | None = Field(None, description="Description of the pet")
    birth_date: datetime | None = Field(None, description="Birth date of the pet")
    owner_id: str = Field(..., description="ID of the pet owner")
    breed_id: str = Field(..., description="ID of the pet breed")
    gender: GenderEnum = Field(default=GenderEnum.UNKNOWN, description="Gender of the pet")
    extra_gene_list: list[MorphGeneMapping | None] = Field(default=[], description="List of extra genes")
    morphology_id: str | None = Field(None, description="ID of the pet morphology")
    picture_list: list[Picture | None] = Field(default=[], description="List of pictures")
    
    def change_owner(self, new_owner_id: str) -> None:
        """Change the owner of the pet and emit domain event."""
        if not new_owner_id:
            raise ValueError("Owner ID cannot be empty")
            
        old_owner_id = self.owner_id
        self.owner_id = new_owner_id
        self._update_timestamp()
        
        # Emit domain event
        from domain.pets.events import PetOwnershipChangedEvent
        self._add_domain_event(PetOwnershipChangedEvent(
            pet_id=self.id,
            old_owner_id=old_owner_id,
            new_owner_id=new_owner_id
        ))
    
    def update_morphology(self, morphology_id: str | None) -> None:
        """Update the morphology of the pet and emit domain event."""
        self.morphology_id = morphology_id
        self._update_timestamp()
        
        # Emit domain event
        from domain.pets.events import PetMorphologyUpdatedEvent
        self._add_domain_event(PetMorphologyUpdatedEvent(
            pet_id=self.id,
            morphology_id=morphology_id
        ))
