"""
依赖注入模块
提供应用程序的各种依赖项
"""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from application.breeds.handlers import BreedService
from application.pets.command_handlers import (
    CreatePetHandler,
    DeletePetHandler,
    TransferPetOwnershipHandler,
    UpdatePetHandler,
)
from application.pets.handlers import PetService
from application.pets.query_handlers import PetQueryService
from application.users.handlers import UserService
from domain.common.event_publisher import EventPublisher, get_event_publisher
from domain.pets.services import PetDomainService
from infrastructure.persistence.postgres.init_db import async_engine
from infrastructure.persistence.postgres.mappers.breed_mapper import BreedMapper
from infrastructure.persistence.postgres.mappers.gene_mapper import GeneMapper
from infrastructure.persistence.postgres.mappers.morph_gene_mapping_mapper import (
    MorphGeneMappingMapper,
)
from infrastructure.persistence.postgres.mappers.morphology_mapper import (
    MorphologyMapper,
)
from infrastructure.persistence.postgres.mappers.pet_mapper import PetMapper
from infrastructure.persistence.postgres.mappers.user_mapper import UserMapper
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


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话（开启事务，自动提交/回滚）"""
    async with AsyncSession(async_engine, expire_on_commit=False) as session:
        async with session.begin():
            yield session

# 数据库相关依赖
async def get_user_mapper() -> UserMapper:
    """获取用户映射器实例"""
    return UserMapper()

async def get_pet_mapper() -> PetMapper:
    """获取宠物映射器实例"""
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


async def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
    mapper: UserMapper = Depends(get_user_mapper),
) -> PostgreSQLUserRepositoryImpl:
    """获取用户仓储实例"""
    return PostgreSQLUserRepositoryImpl(session, mapper)

async def get_pet_repository(
    session: AsyncSession = Depends(get_db_session),
    mapper: PetMapper = Depends(get_pet_mapper),
    event_publisher: EventPublisher = Depends(get_event_publisher),
) -> PostgreSQLPetRepositoryImpl:
    """获取宠物仓储实例"""
    return PostgreSQLPetRepositoryImpl(session, mapper, event_publisher)


async def get_breed_repository(
    session: AsyncSession = Depends(get_db_session),
    mapper: BreedMapper = Depends(lambda: BreedMapper()),
) -> PostgreSQLBreedRepositoryImpl:
    """获取品种仓储实例"""
    return PostgreSQLBreedRepositoryImpl(session, mapper)


async def get_morphology_repository(
    session: AsyncSession = Depends(get_db_session),
    mapper: MorphologyMapper = Depends(lambda: MorphologyMapper(MorphGeneMappingMapper(GeneMapper()))),
) -> PostgreSQLMorphologyRepositoryImpl:
    """获取形态学仓储实例"""
    return PostgreSQLMorphologyRepositoryImpl(session, mapper)


async def get_user_service(
    user_repository: PostgreSQLUserRepositoryImpl = Depends(get_user_repository),
) -> UserService:
    """获取用户服务实例"""
    return UserService(user_repository)

async def get_pet_service(
    pet_repository: PostgreSQLPetRepositoryImpl = Depends(get_pet_repository),
    user_repository: PostgreSQLUserRepositoryImpl = Depends(get_user_repository),
    breed_repository: PostgreSQLBreedRepositoryImpl = Depends(get_breed_repository),
) -> PetService:
    """获取宠物服务实例"""
    return PetService(pet_repository, user_repository, breed_repository)


async def get_breed_service(
    breed_repository: PostgreSQLBreedRepositoryImpl = Depends(get_breed_repository),
) -> BreedService:
    """获取品种服务实例"""
    return BreedService(breed_repository)


async def get_pet_domain_service(
    pet_repository: PostgreSQLPetRepositoryImpl = Depends(get_pet_repository),
    user_repository: PostgreSQLUserRepositoryImpl = Depends(get_user_repository),
    breed_repository: PostgreSQLBreedRepositoryImpl = Depends(get_breed_repository),
    morphology_repository: PostgreSQLMorphologyRepositoryImpl = Depends(get_morphology_repository),
) -> PetDomainService:
    """获取宠物领域服务实例"""
    return PetDomainService(
        pet_repository=pet_repository,
        user_repository=user_repository,
        breed_repository=breed_repository,
        morphology_repository=morphology_repository,
    )


async def get_pet_query_service(
    pet_repository: PostgreSQLPetRepositoryImpl = Depends(get_pet_repository),
    user_repository: PostgreSQLUserRepositoryImpl = Depends(get_user_repository),
    breed_repository: PostgreSQLBreedRepositoryImpl = Depends(get_breed_repository),
    morphology_repository: PostgreSQLMorphologyRepositoryImpl = Depends(get_morphology_repository),
) -> PetQueryService:
    """获取宠物查询服务实例"""
    return PetQueryService(
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
    """获取创建宠物命令处理器实例"""
    return CreatePetHandler(
        pet_repository=pet_repository,
        user_repository=user_repository,
        breed_repository=breed_repository,
        pet_domain_service=pet_domain_service,
    )


async def get_transfer_pet_ownership_handler(
    pet_repository: PostgreSQLPetRepositoryImpl = Depends(get_pet_repository),
    user_repository: PostgreSQLUserRepositoryImpl = Depends(get_user_repository),
    pet_domain_service: PetDomainService = Depends(get_pet_domain_service),
) -> TransferPetOwnershipHandler:
    """获取转移宠物所有权命令处理器实例"""
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
    """获取更新宠物命令处理器实例"""
    return UpdatePetHandler(
        pet_repository=pet_repository,
        breed_repository=breed_repository,
        pet_domain_service=pet_domain_service,
    )


async def get_delete_pet_handler(
    pet_repository: PostgreSQLPetRepositoryImpl = Depends(get_pet_repository),
) -> DeletePetHandler:
    """获取删除宠物命令处理器实例"""
    return DeletePetHandler(pet_repository=pet_repository)


# 可以添加其他服务的依赖函数
# async def get_auth_service(
#     user_service: UserService = Depends(get_user_service),
# ) -> AuthService:
#     """获取认证服务实例"""
#     return AuthService(user_service)

# async def get_notification_service() -> NotificationService:
#     """获取通知服务实例"""
#     return NotificationService()
