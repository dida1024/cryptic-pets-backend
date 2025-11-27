"""Breed dependency module.

Provides breed-related command handlers and query services.
"""

from fastapi import Depends

from application.breeds.command_handlers import (
    CreateBreedHandler,
    DeleteBreedHandler,
    UpdateBreedHandler,
)
from application.breeds.query_handlers import BreedQueryService
from infrastructure.dependencies.repositories import (
    get_breed_repository,
    get_pet_repository,
)
from infrastructure.persistence.postgres.repositories.breed_repository_impl import (
    PostgreSQLBreedRepositoryImpl,
)
from infrastructure.persistence.postgres.repositories.pet_repository_impl import (
    PostgreSQLPetRepositoryImpl,
)


async def get_create_breed_handler(
    breed_repository: PostgreSQLBreedRepositoryImpl = Depends(get_breed_repository),
) -> CreateBreedHandler:
    """Get create breed command handler instance.

    Args:
        breed_repository: Breed repository.

    Returns:
        CreateBreedHandler: Handler for creating breeds.
    """
    return CreateBreedHandler(breed_repository)


async def get_update_breed_handler(
    breed_repository: PostgreSQLBreedRepositoryImpl = Depends(get_breed_repository),
) -> UpdateBreedHandler:
    """Get update breed command handler instance.

    Args:
        breed_repository: Breed repository.

    Returns:
        UpdateBreedHandler: Handler for updating breeds.
    """
    return UpdateBreedHandler(breed_repository)


async def get_delete_breed_handler(
    breed_repository: PostgreSQLBreedRepositoryImpl = Depends(get_breed_repository),
) -> DeleteBreedHandler:
    """Get delete breed command handler instance.

    Args:
        breed_repository: Breed repository.

    Returns:
        DeleteBreedHandler: Handler for deleting breeds.
    """
    return DeleteBreedHandler(breed_repository)


async def get_breed_query_service(
    breed_repository: PostgreSQLBreedRepositoryImpl = Depends(get_breed_repository),
    pet_repository: PostgreSQLPetRepositoryImpl = Depends(get_pet_repository),
) -> BreedQueryService:
    """Get breed query service instance.

    Args:
        breed_repository: Breed repository.
        pet_repository: Pet repository for breed usage queries.

    Returns:
        BreedQueryService: Service for querying breeds.
    """
    return BreedQueryService(breed_repository, pet_repository)

