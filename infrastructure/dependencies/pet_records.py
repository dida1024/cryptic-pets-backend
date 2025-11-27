"""Pet records dependency module.

Provides pet record-related command handlers and query services.
"""

from fastapi import Depends

from application.pet_records.command_handlers import (
    CreatePetRecordHandler,
    DeletePetRecordHandler,
    UpdatePetRecordHandler,
)
from application.pet_records.query_handlers import PetRecordQueryService
from infrastructure.dependencies.repositories import get_pet_record_repository
from infrastructure.persistence.postgres.repositories.pet_record_repository_impl import (
    PostgreSQLPetRecordRepositoryImpl,
)


async def get_create_pet_record_handler(
    pet_record_repository: PostgreSQLPetRecordRepositoryImpl = Depends(
        get_pet_record_repository
    ),
) -> CreatePetRecordHandler:
    """Get create pet record command handler instance.

    Args:
        pet_record_repository: Pet record repository.

    Returns:
        CreatePetRecordHandler: Handler for creating pet records.
    """
    return CreatePetRecordHandler(pet_record_repository)


async def get_update_pet_record_handler(
    pet_record_repository: PostgreSQLPetRecordRepositoryImpl = Depends(
        get_pet_record_repository
    ),
) -> UpdatePetRecordHandler:
    """Get update pet record command handler instance.

    Args:
        pet_record_repository: Pet record repository.

    Returns:
        UpdatePetRecordHandler: Handler for updating pet records.
    """
    return UpdatePetRecordHandler(pet_record_repository)


async def get_delete_pet_record_handler(
    pet_record_repository: PostgreSQLPetRecordRepositoryImpl = Depends(
        get_pet_record_repository
    ),
) -> DeletePetRecordHandler:
    """Get delete pet record command handler instance.

    Args:
        pet_record_repository: Pet record repository.

    Returns:
        DeletePetRecordHandler: Handler for deleting pet records.
    """
    return DeletePetRecordHandler(pet_record_repository)


async def get_pet_record_query_service(
    pet_record_repository: PostgreSQLPetRecordRepositoryImpl = Depends(
        get_pet_record_repository
    ),
) -> PetRecordQueryService:
    """Get pet record query service instance.

    Args:
        pet_record_repository: Pet record repository.

    Returns:
        PetRecordQueryService: Service for querying pet records.
    """
    return PetRecordQueryService(pet_record_repository)

