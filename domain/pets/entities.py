"""Pet domain entities with rich domain behavior."""

from datetime import date, datetime

from pydantic import Field

from domain.base_entity import BaseEntity
from domain.common.aggregate_root import AggregateRoot
from domain.common.entities import I18n, Picture
from domain.pets.pet_age import PetAge
from domain.pets.value_objects import (
    GenderEnum,
    GeneCategoryEnum,
    InheritanceTypeEnum,
    ZygosityEnum,
)


class Breed(AggregateRoot):
    """Breed entity representing a breed in the system.

    This is an aggregate root as breeds are managed independently.
    """

    name: I18n = Field(..., description="Name of the breed keyed by locale")
    description: I18n | None = Field(
        default=None, description="Description of the breed keyed by locale"
    )
    picture_list: list[Picture | None] = Field(default=[], description="List of pictures")

    def update_name(self, name: I18n) -> None:
        """Update the breed name."""
        self.name = name
        self._update_timestamp()

        from domain.pets.events import BreedUpdatedEvent

        self.add_domain_event(
            BreedUpdatedEvent(
                breed_id=self.id,
                name=self.name,
            )
        )

    def update_description(self, description: I18n | None) -> None:
        """Update the breed description."""
        self.description = description
        self._update_timestamp()

    def add_picture(self, picture: Picture) -> None:
        """Add a picture to the breed."""
        self.picture_list.append(picture)
        self._update_timestamp()

    def remove_picture(self, picture_id: str) -> bool:
        """Remove a picture from the breed.

        Returns:
            True if picture was found and removed, False otherwise.
        """
        for i, pic in enumerate(self.picture_list):
            if pic and pic.id == picture_id:
                self.picture_list.pop(i)
                self._update_timestamp()
                return True
        return False


class Gene(AggregateRoot):
    """Gene entity representing a gene in the system.

    This is an aggregate root as genes are managed independently.
    """

    name: I18n = Field(..., description="Name of the gene keyed by locale")
    alias: I18n | None = Field(
        default=None, description="Alias of the gene keyed by locale"
    )
    description: I18n | None = Field(
        default=None, description="Description of the gene keyed by locale"
    )
    notation: str | None = Field(default=None, description="Notation of the gene")
    inheritance_type: InheritanceTypeEnum | None = Field(
        default=None, description="Inheritance type of the gene"
    )
    category: GeneCategoryEnum | None = Field(
        default=None, description="Category of the gene"
    )
    picture_list: list[Picture | None] = Field(default=[], description="List of pictures")

    def update_details(
        self,
        name: I18n | None = None,
        alias: I18n | None = None,
        description: I18n | None = None,
        notation: str | None = None,
        inheritance_type: InheritanceTypeEnum | None = None,
        category: GeneCategoryEnum | None = None,
    ) -> None:
        """Update gene details."""
        if name is not None:
            self.name = name
        if alias is not None:
            self.alias = alias
        if description is not None:
            self.description = description
        if notation is not None:
            self.notation = notation
        if inheritance_type is not None:
            self.inheritance_type = inheritance_type
        if category is not None:
            self.category = category
        self._update_timestamp()

    def add_picture(self, picture: Picture) -> None:
        """Add a picture to the gene."""
        self.picture_list.append(picture)
        self._update_timestamp()


class MorphGeneMapping(BaseEntity):
    """Entity representing a gene mapping for a morphology or pet.

    This is NOT an aggregate root - it's an entity within Pet or Morphology aggregates.
    """

    gene_id: str = Field(..., description="ID of the gene in this morphology/pet")
    zygosity: ZygosityEnum = Field(
        default=ZygosityEnum.UNKNOWN, description="homozygous / heterozygous / unknown"
    )
    is_required: bool = Field(
        default=True, description="Is this gene required for the morphology expression"
    )


class Morphology(AggregateRoot):
    """Morphology entity representing a morphology in the system.

    This is an aggregate root as morphologies are managed independently.
    """

    name: I18n = Field(..., description="Name of the morphology keyed by locale")
    description: I18n | None = Field(
        default=None, description="Description of the morphology keyed by locale"
    )
    gene_mapping_ids: list[str] = Field(
        default=[], description="List of gene mapping IDs"
    )
    picture_list: list[Picture | None] = Field(default=[], description="List of pictures")

    def update_name(self, name: I18n) -> None:
        """Update the morphology name."""
        self.name = name
        self._update_timestamp()

    def update_description(self, description: I18n | None) -> None:
        """Update the morphology description."""
        self.description = description
        self._update_timestamp()

    def add_gene_mapping(self, gene_mapping_id: str) -> None:
        """Add a gene mapping to the morphology."""
        if gene_mapping_id not in self.gene_mapping_ids:
            self.gene_mapping_ids.append(gene_mapping_id)
            self._update_timestamp()

    def remove_gene_mapping(self, gene_mapping_id: str) -> bool:
        """Remove a gene mapping from the morphology.

        Returns:
            True if mapping was found and removed, False otherwise.
        """
        if gene_mapping_id in self.gene_mapping_ids:
            self.gene_mapping_ids.remove(gene_mapping_id)
            self._update_timestamp()
            return True
        return False

    def add_picture(self, picture: Picture) -> None:
        """Add a picture to the morphology."""
        self.picture_list.append(picture)
        self._update_timestamp()


class Pet(AggregateRoot):
    """Pet entity representing a pet in the system.

    This is an aggregate root that encapsulates pet-related business logic.
    """

    name: str = Field(..., description="Name of the pet")
    description: str | None = Field(None, description="Description of the pet")
    birth_date: datetime | None = Field(None, description="Birth date of the pet")
    owner_id: str = Field(..., description="ID of the pet owner")
    breed_id: str = Field(..., description="ID of the pet breed")
    gender: GenderEnum = Field(
        default=GenderEnum.UNKNOWN, description="Gender of the pet"
    )
    extra_gene_list: list[MorphGeneMapping | None] = Field(
        default=[], description="List of extra genes"
    )
    morphology_id: str | None = Field(None, description="ID of the pet morphology")
    picture_list: list[Picture | None] = Field(default=[], description="List of pictures")

    # ========== Business Methods ==========

    def change_owner(self, new_owner_id: str) -> None:
        """Change the owner of the pet and emit domain event.

        Args:
            new_owner_id: The ID of the new owner.

        Raises:
            ValueError: If new_owner_id is empty.

        Emits:
            PetOwnershipChangedEvent: When ownership is changed.
        """
        if not new_owner_id:
            raise ValueError("Owner ID cannot be empty")

        old_owner_id = self.owner_id
        self.owner_id = new_owner_id
        self._update_timestamp()

        from domain.pets.events import PetOwnershipChangedEvent

        self.add_domain_event(
            PetOwnershipChangedEvent(
                pet_id=self.id,
                old_owner_id=old_owner_id,
                new_owner_id=new_owner_id,
            )
        )

    def update_morphology(self, morphology_id: str | None) -> None:
        """Update the morphology of the pet and emit domain event.

        Args:
            morphology_id: The new morphology ID (or None to clear).

        Emits:
            PetMorphologyUpdatedEvent: When morphology is updated.
        """
        self.morphology_id = morphology_id
        self._update_timestamp()

        from domain.pets.events import PetMorphologyUpdatedEvent

        self.add_domain_event(
            PetMorphologyUpdatedEvent(
                pet_id=self.id,
                morphology_id=morphology_id,
            )
        )

    def add_gene_mapping(self, gene_mapping: MorphGeneMapping) -> None:
        """Add a gene mapping to the pet.

        Args:
            gene_mapping: The gene mapping to add.
        """
        # Check if gene already exists
        for existing in self.extra_gene_list:
            if existing and existing.gene_id == gene_mapping.gene_id:
                # Update existing mapping
                existing.zygosity = gene_mapping.zygosity
                existing.is_required = gene_mapping.is_required
                self._update_timestamp()
                return

        self.extra_gene_list.append(gene_mapping)
        self._update_timestamp()

    def remove_gene_mapping(self, gene_id: str) -> bool:
        """Remove a gene mapping from the pet.

        Args:
            gene_id: The ID of the gene to remove.

        Returns:
            True if gene was found and removed, False otherwise.
        """
        for i, mapping in enumerate(self.extra_gene_list):
            if mapping and mapping.gene_id == gene_id:
                self.extra_gene_list.pop(i)
                self._update_timestamp()
                return True
        return False

    def add_picture(self, picture: Picture) -> None:
        """Add a picture to the pet.

        Args:
            picture: The picture to add.
        """
        self.picture_list.append(picture)
        self._update_timestamp()

    def remove_picture(self, picture_id: str) -> bool:
        """Remove a picture from the pet.

        Args:
            picture_id: The ID of the picture to remove.

        Returns:
            True if picture was found and removed, False otherwise.
        """
        for i, pic in enumerate(self.picture_list):
            if pic and pic.id == picture_id:
                self.picture_list.pop(i)
                self._update_timestamp()
                return True
        return False

    def set_birth_date(self, birth_date: datetime | date | None) -> None:
        """Set the birth date of the pet with validation.

        Args:
            birth_date: The birth date to set.

        Raises:
            ValueError: If birth date is in the future or too far in the past.
        """
        if birth_date is not None:
            # Convert date to datetime if needed
            if isinstance(birth_date, date) and not isinstance(birth_date, datetime):
                birth_date = datetime.combine(birth_date, datetime.min.time())

            # Validate using PetAge value object (validation happens in constructor)
            PetAge.from_birth_date(birth_date)

        self.birth_date = birth_date
        self._update_timestamp()

    def update_name(self, name: str) -> None:
        """Update the pet's name.

        Args:
            name: The new name.
        """
        if name != self.name:
            self.name = name
            self._update_timestamp()

    def update_description(self, description: str | None) -> None:
        """Update the pet's description.

        Args:
            description: The new description.
        """
        if description != self.description:
            self.description = description
            self._update_timestamp()

    def update_gender(self, gender: GenderEnum) -> None:
        """Update the pet's gender.

        Args:
            gender: The new gender.
        """
        if gender != self.gender:
            self.gender = gender
            self._update_timestamp()

    def update_breed(self, breed_id: str) -> None:
        """Update the pet's breed.

        Args:
            breed_id: The ID of the new breed.
        """
        if breed_id != self.breed_id:
            self.breed_id = breed_id
            self._update_timestamp()

    # ========== Query Methods ==========

    def get_pet_age(self) -> PetAge:
        """Get the pet's age as a PetAge value object.

        Returns:
            PetAge value object with age calculation methods.
        """
        return PetAge.from_birth_date(self.birth_date)

    def calculate_age_in_years(self) -> int | None:
        """Calculate the pet's age in years.

        Returns:
            Age in years, or None if birth date is unknown.
        """
        return self.get_pet_age().get_age_in_years()

    def calculate_age_in_months(self) -> int | None:
        """Calculate the pet's age in months.

        Returns:
            Age in months, or None if birth date is unknown.
        """
        return self.get_pet_age().get_age_in_months()

    def is_adult(self) -> bool:
        """Check if the pet is an adult (1 year or older).

        Returns:
            True if pet is adult, False if puppy or unknown.
        """
        return self.get_pet_age().is_adult()

    def is_puppy(self) -> bool:
        """Check if the pet is a puppy (less than 1 year old).

        Returns:
            True if pet is a puppy, False if adult or unknown.
        """
        return self.get_pet_age().is_puppy()

    def is_senior(self, senior_age: int = 7) -> bool:
        """Check if the pet is a senior.

        Args:
            senior_age: Age threshold for senior classification (default 7).

        Returns:
            True if pet is senior, False otherwise or if unknown.
        """
        return self.get_pet_age().is_senior(senior_age)

    def get_life_stage(self) -> str | None:
        """Get the pet's life stage.

        Returns:
            Life stage string ('puppy', 'young_adult', 'adult', 'senior')
            or None if birth date is unknown.
        """
        return self.get_pet_age().get_life_stage()

    def get_formatted_age(self) -> str:
        """Get a formatted age string.

        Returns:
            Human-readable age string.
        """
        return self.get_pet_age().get_formatted_age() or "Unknown"

    def has_gene(self, gene_id: str) -> bool:
        """Check if the pet has a specific gene.

        Args:
            gene_id: The ID of the gene to check.

        Returns:
            True if pet has the gene, False otherwise.
        """
        return any(m and m.gene_id == gene_id for m in self.extra_gene_list)

    def get_gene_mapping(self, gene_id: str) -> MorphGeneMapping | None:
        """Get a specific gene mapping.

        Args:
            gene_id: The ID of the gene to find.

        Returns:
            The gene mapping if found, None otherwise.
        """
        for mapping in self.extra_gene_list:
            if mapping and mapping.gene_id == gene_id:
                return mapping
        return None
