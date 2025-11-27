"""Pet dependency module.

Provides pet-related command handlers, query services, and domain services.
"""

from fastapi import Depends

from application.pets.command_handlers import (
    CreatePetHandler,
    DeletePetHandler,
    TransferPetOwnershipHandler,
    UpdatePetHandler,
)
from application.pets.query_handlers import PetQueryService
from application.pets.read_models import PetSearchReadRepository
from domain.pets.services import PetDomainService
from infrastructure.dependencies.repositories import (
    get_breed_repository,
    get_morphology_repository,
    get_pet_repository,
    get_pet_search_repository,
    get_user_repository,
)
from infrastructure.persistence.postgres.repositories.breed_repository_impl import (
    PostgreSQLBreedRepositoryImpl,
)
from infrastructure.persistence.postgres.repositories.morphology_repository_impl import (
    PostgreSQLMorphologyRepositoryImpl,
)
from infrastructure.persistence.postgres.repositories.pet_repository_impl import (
    PostgreSQLPetRepositoryImpl,
)
from infrastructure.persistence.postgres.repositories.user_repository_impl import (
    PostgreSQLUserRepositoryImpl,
)


async def get_pet_domain_service(
    pet_repository: PostgreSQLPetRepositoryImpl = Depends(get_pet_repository),
    user_repository: PostgreSQLUserRepositoryImpl = Depends(get_user_repository),
    breed_repository: PostgreSQLBreedRepositoryImpl = Depends(get_breed_repository),
    morphology_repository: PostgreSQLMorphologyRepositoryImpl = Depends(
        get_morphology_repository
    ),
) -> PetDomainService:
    """Get pet domain service instance.

    Args:
        pet_repository: Pet repository.
        user_repository: User repository.
        breed_repository: Breed repository.
        morphology_repository: Morphology repository.

    Returns:
        PetDomainService: Domain service for pet operations.
    """
    return PetDomainService(
        pet_repository=pet_repository,
        user_repository=user_repository,
        breed_repository=breed_repository,
        morphology_repository=morphology_repository,
    )


async def get_create_pet_handler(
    pet_repository: PostgreSQLPetRepositoryImpl = Depends(get_pet_repository),
    user_repository: PostgreSQLUserRepositoryImpl = Depends(get_user_repository),
    breed_repository: PostgreSQLBreedRepositoryImpl = Depends(get_breed_repository),
    pet_domain_service: PetDomainService = Depends(get_pet_domain_service),
) -> CreatePetHandler:
    """Get create pet command handler instance.

    Args:
        pet_repository: Pet repository.
        user_repository: User repository.
        breed_repository: Breed repository.
        pet_domain_service: Pet domain service.

    Returns:
        CreatePetHandler: Handler for creating pets.
    """
    return CreatePetHandler(
        pet_repository, user_repository, breed_repository, pet_domain_service
    )


async def get_transfer_pet_ownership_handler(
    pet_repository: PostgreSQLPetRepositoryImpl = Depends(get_pet_repository),
    user_repository: PostgreSQLUserRepositoryImpl = Depends(get_user_repository),
    pet_domain_service: PetDomainService = Depends(get_pet_domain_service),
) -> TransferPetOwnershipHandler:
    """Get transfer pet ownership command handler instance.

    Args:
        pet_repository: Pet repository.
        user_repository: User repository.
        pet_domain_service: Pet domain service.

    Returns:
        TransferPetOwnershipHandler: Handler for transferring pet ownership.
    """
    return TransferPetOwnershipHandler(
        pet_repository=pet_repository,
        user_repository=user_repository,
        pet_domain_service=pet_domain_service,
    )


async def get_update_pet_handler(
    pet_repository: PostgreSQLPetRepositoryImpl = Depends(get_pet_repository),
    breed_repository: PostgreSQLBreedRepositoryImpl = Depends(get_breed_repository),
    pet_domain_service: PetDomainService = Depends(get_pet_domain_service),
) -> UpdatePetHandler:
    """Get update pet command handler instance.

    Args:
        pet_repository: Pet repository.
        breed_repository: Breed repository.
        pet_domain_service: Pet domain service.

    Returns:
        UpdatePetHandler: Handler for updating pets.
    """
    return UpdatePetHandler(
        pet_repository=pet_repository,
        breed_repository=breed_repository,
        pet_domain_service=pet_domain_service,
    )


async def get_delete_pet_handler(
    pet_repository: PostgreSQLPetRepositoryImpl = Depends(get_pet_repository),
) -> DeletePetHandler:
    """Get delete pet command handler instance.

    Args:
        pet_repository: Pet repository.

    Returns:
        DeletePetHandler: Handler for deleting pets.
    """
    return DeletePetHandler(pet_repository=pet_repository)


async def get_pet_query_service(
    pet_repository: PostgreSQLPetRepositoryImpl = Depends(get_pet_repository),
    pet_search_repository: PetSearchReadRepository = Depends(get_pet_search_repository),
    user_repository: PostgreSQLUserRepositoryImpl = Depends(get_user_repository),
    breed_repository: PostgreSQLBreedRepositoryImpl = Depends(get_breed_repository),
    morphology_repository: PostgreSQLMorphologyRepositoryImpl = Depends(
        get_morphology_repository
    ),
) -> PetQueryService:
    """Get pet query service instance.

    Args:
        pet_repository: Pet repository.
        pet_search_repository: Pet search repository.
        user_repository: User repository.
        breed_repository: Breed repository.
        morphology_repository: Morphology repository.

    Returns:
        PetQueryService: Service for querying pets.
    """
    return PetQueryService(
        pet_repository,
        pet_search_repository,
        user_repository,
        breed_repository,
        morphology_repository,
    )

