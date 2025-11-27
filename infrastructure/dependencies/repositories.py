"""Repository dependency module.

Provides repository dependencies for data access.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from application.pets.read_models import PetSearchReadRepository
from domain.common.event_publisher import EventPublisher
from infrastructure.dependencies.database import get_db_session
from infrastructure.dependencies.events import get_event_publisher
from infrastructure.dependencies.mappers import (
    get_breed_mapper,
    get_morphology_mapper,
    get_pet_mapper,
    get_pet_record_mapper,
    get_user_mapper,
)
from infrastructure.persistence.postgres.mappers.breed_mapper import BreedMapper
from infrastructure.persistence.postgres.mappers.morphology_mapper import (
    MorphologyMapper,
)
from infrastructure.persistence.postgres.mappers.pet_mapper import PetMapper
from infrastructure.persistence.postgres.mappers.pet_record_mapper import (
    PetRecordMapper,
)
from infrastructure.persistence.postgres.mappers.user_mapper import UserMapper
from infrastructure.persistence.postgres.repositories.breed_repository_impl import (
    PostgreSQLBreedRepositoryImpl,
)
from infrastructure.persistence.postgres.repositories.morphology_repository_impl import (
    PostgreSQLMorphologyRepositoryImpl,
)
from infrastructure.persistence.postgres.repositories.pet_record_repository_impl import (
    PostgreSQLPetRecordRepositoryImpl,
)
from infrastructure.persistence.postgres.repositories.pet_repository_impl import (
    PostgreSQLPetRepositoryImpl,
)
from infrastructure.persistence.postgres.repositories.pet_search_read_repository import (
    PostgreSQLPetSearchReadRepository,
)
from infrastructure.persistence.postgres.repositories.user_repository_impl import (
    PostgreSQLUserRepositoryImpl,
)


async def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
    mapper: UserMapper = Depends(get_user_mapper),
    event_publisher: EventPublisher = Depends(get_event_publisher),
) -> PostgreSQLUserRepositoryImpl:
    """Get user repository instance.

    Args:
        session: Database session.
        mapper: User mapper.
        event_publisher: Event publisher for domain events.

    Returns:
        PostgreSQLUserRepositoryImpl: User repository implementation.
    """
    return PostgreSQLUserRepositoryImpl(session, mapper, event_publisher)


async def get_pet_repository(
    session: AsyncSession = Depends(get_db_session),
    mapper: PetMapper = Depends(get_pet_mapper),
    event_publisher: EventPublisher = Depends(get_event_publisher),
) -> PostgreSQLPetRepositoryImpl:
    """Get pet repository instance.

    Args:
        session: Database session.
        mapper: Pet mapper.
        event_publisher: Event publisher for domain events.

    Returns:
        PostgreSQLPetRepositoryImpl: Pet repository implementation.
    """
    return PostgreSQLPetRepositoryImpl(session, mapper, event_publisher)


async def get_pet_search_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PetSearchReadRepository:
    """Get pet search read repository instance.

    Args:
        session: Database session.

    Returns:
        PetSearchReadRepository: Pet search repository for read operations.
    """
    return PostgreSQLPetSearchReadRepository(session)


async def get_breed_repository(
    session: AsyncSession = Depends(get_db_session),
    mapper: BreedMapper = Depends(get_breed_mapper),
    event_publisher: EventPublisher = Depends(get_event_publisher),
) -> PostgreSQLBreedRepositoryImpl:
    """Get breed repository instance.

    Args:
        session: Database session.
        mapper: Breed mapper.
        event_publisher: Event publisher for domain events.

    Returns:
        PostgreSQLBreedRepositoryImpl: Breed repository implementation.
    """
    return PostgreSQLBreedRepositoryImpl(session, mapper, event_publisher)


async def get_morphology_repository(
    session: AsyncSession = Depends(get_db_session),
    mapper: MorphologyMapper = Depends(get_morphology_mapper),
) -> PostgreSQLMorphologyRepositoryImpl:
    """Get morphology repository instance.

    Args:
        session: Database session.
        mapper: Morphology mapper.

    Returns:
        PostgreSQLMorphologyRepositoryImpl: Morphology repository implementation.
    """
    return PostgreSQLMorphologyRepositoryImpl(session, mapper)


async def get_pet_record_repository(
    session: AsyncSession = Depends(get_db_session),
    mapper: PetRecordMapper = Depends(get_pet_record_mapper),
    event_publisher: EventPublisher = Depends(get_event_publisher),
) -> PostgreSQLPetRecordRepositoryImpl:
    """Get pet record repository instance.

    Args:
        session: Database session.
        mapper: Pet record mapper.
        event_publisher: Event publisher for domain events.

    Returns:
        PostgreSQLPetRecordRepositoryImpl: Pet record repository implementation.
    """
    return PostgreSQLPetRecordRepositoryImpl(session, mapper, event_publisher)

