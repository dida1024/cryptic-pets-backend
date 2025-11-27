"""Mapper dependency module.

Provides entity-to-model mapper dependencies.
"""

from infrastructure.persistence.postgres.mappers.breed_mapper import BreedMapper
from infrastructure.persistence.postgres.mappers.gene_mapper import GeneMapper
from infrastructure.persistence.postgres.mappers.morph_gene_mapping_mapper import (
    MorphGeneMappingMapper,
)
from infrastructure.persistence.postgres.mappers.morphology_mapper import (
    MorphologyMapper,
)
from infrastructure.persistence.postgres.mappers.pet_mapper import PetMapper
from infrastructure.persistence.postgres.mappers.pet_record_mapper import (
    PetRecordMapper,
)
from infrastructure.persistence.postgres.mappers.user_mapper import UserMapper


async def get_user_mapper() -> UserMapper:
    """Get user mapper instance.

    Returns:
        UserMapper: Mapper for User entity to model conversion.
    """
    return UserMapper()


async def get_breed_mapper() -> BreedMapper:
    """Get breed mapper instance.

    Returns:
        BreedMapper: Mapper for Breed entity to model conversion.
    """
    return BreedMapper()


async def get_gene_mapper() -> GeneMapper:
    """Get gene mapper instance.

    Returns:
        GeneMapper: Mapper for Gene entity to model conversion.
    """
    return GeneMapper()


async def get_morph_gene_mapping_mapper(
    gene_mapper: GeneMapper | None = None,
) -> MorphGeneMappingMapper:
    """Get morph gene mapping mapper instance.

    Args:
        gene_mapper: Optional gene mapper, creates new one if not provided.

    Returns:
        MorphGeneMappingMapper: Mapper for MorphGeneMapping entity to model conversion.
    """
    if gene_mapper is None:
        gene_mapper = GeneMapper()
    return MorphGeneMappingMapper(gene_mapper)


async def get_morphology_mapper(
    morph_gene_mapping_mapper: MorphGeneMappingMapper | None = None,
) -> MorphologyMapper:
    """Get morphology mapper instance.

    Args:
        morph_gene_mapping_mapper: Optional mapping mapper, creates new one if not provided.

    Returns:
        MorphologyMapper: Mapper for Morphology entity to model conversion.
    """
    if morph_gene_mapping_mapper is None:
        morph_gene_mapping_mapper = MorphGeneMappingMapper(GeneMapper())
    return MorphologyMapper(morph_gene_mapping_mapper)


async def get_pet_mapper() -> PetMapper:
    """Get pet mapper instance.

    Returns:
        PetMapper: Mapper for Pet entity to model conversion.
    """
    breed_mapper = BreedMapper()
    gene_mapper = GeneMapper()
    morph_gene_mapping_mapper = MorphGeneMappingMapper(gene_mapper)
    morphology_mapper = MorphologyMapper(morph_gene_mapping_mapper)
    user_mapper = UserMapper()
    return PetMapper(
        breed_mapper=breed_mapper,
        morphology_mapper=morphology_mapper,
        gene_mapping_mapper=morph_gene_mapping_mapper,
        user_mapper=user_mapper,
    )


async def get_pet_record_mapper() -> PetRecordMapper:
    """Get pet record mapper instance.

    Returns:
        PetRecordMapper: Mapper for PetRecord entity to model conversion.
    """
    return PetRecordMapper()

