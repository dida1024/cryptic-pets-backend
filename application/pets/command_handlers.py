"""
宠物命令处理器
实现CQRS模式的命令部分，处理写操作
"""

from loguru import logger

from domain.pets.entities import Pet
from domain.pets.exceptions import (
    BreedNotFoundError,
    DuplicatePetNameError,
    PetNotFoundError,
)
from domain.pets.repository import BreedRepository, PetRepository
from domain.pets.services import PetDomainService, CreatePetData
from domain.users.exceptions import UserNotFoundError
from domain.users.repository import UserRepository
from application.pets.commands import (
    CreatePetCommand,
    DeletePetCommand,
    TransferPetOwnershipCommand,
    UpdatePetCommand,
)


class CreatePetHandler:
    """创建宠物命令处理器"""
    
    def __init__(
        self,
        pet_repository: PetRepository,
        user_repository: UserRepository,
        breed_repository: BreedRepository,
        pet_domain_service: PetDomainService = None,
    ):
        self.pet_repository = pet_repository
        self.user_repository = user_repository
        self.breed_repository = breed_repository
        self.pet_domain_service = pet_domain_service
        self.logger = logger
    
    async def handle(self, command: CreatePetCommand) -> Pet:
        """处理创建宠物命令"""
        # 检查宠物名是否已存在
        if await self.pet_repository.exists_by_name(command.name):
            raise DuplicatePetNameError(f"Pet name '{command.name}' already exists")
        
        # 如果有领域服务，使用领域服务创建宠物（包含跨聚合验证）
        if self.pet_domain_service:
            # 创建领域服务所需的数据传输对象
            pet_data = CreatePetData(
                name=command.name,
                description=command.description,
                breed_id=command.breed_id,
                birth_date=command.birth_date,
                gender=command.gender,
                morphology_id=command.morphology_id,
                extra_gene_list=command.extra_gene_list,
            )
            
            # 使用领域服务创建宠物（包含跨聚合验证）
            self.logger.info(f"Creating pet using domain service: {pet_data}")
            return await self.pet_domain_service.create_pet_with_validation(
                pet_data=pet_data,
                owner_id=command.owner_id,
            )
        
        # 如果没有领域服务，使用原来的方式创建宠物
        else:
            # 验证用户和品种存在
            owner = await self.user_repository.get_by_id(command.owner_id)
            if not owner:
                raise UserNotFoundError(f"User with id '{command.owner_id}' not found")
            breed = await self.breed_repository.get_by_id(command.breed_id)
            if not breed:
                raise BreedNotFoundError(f"Breed with id '{command.breed_id}' not found")
                
            # 创建宠物实体
            pet = Pet(
                name=command.name,
                description=command.description,
                owner_id=command.owner_id,
                breed_id=command.breed_id,
                birth_date=command.birth_date,
                gender=command.gender,
            )
            self.logger.info(f"Creating pet: {pet}")

            # 保存宠物
            created_pet = await self.pet_repository.create(pet)
            
            # 添加领域事件
            from domain.pets.events import PetCreatedEvent
            created_pet._add_domain_event(PetCreatedEvent(
                pet_id=created_pet.id,
                owner_id=created_pet.owner_id,
                breed_id=created_pet.breed_id
            ))
            
            return created_pet


class TransferPetOwnershipHandler:
    """转移宠物所有权命令处理器"""
    
    def __init__(
        self,
        pet_repository: PetRepository,
        user_repository: UserRepository,
        pet_domain_service: PetDomainService = None,
    ):
        self.pet_repository = pet_repository
        self.user_repository = user_repository
        self.pet_domain_service = pet_domain_service
        self.logger = logger
    
    async def handle(self, command: TransferPetOwnershipCommand) -> Pet:
        """处理转移宠物所有权命令"""
        # 如果有领域服务，使用领域服务转移所有权（包含业务规则验证）
        if self.pet_domain_service:
            self.logger.info(f"Transferring pet ownership using domain service: {command}")
            return await self.pet_domain_service.transfer_pet_ownership(
                pet_id=command.pet_id,
                new_owner_id=command.new_owner_id,
                current_user_id=command.current_user_id,
            )
        
        # 如果没有领域服务，使用原来的方式转移所有权
        else:
            # 获取宠物
            pet = await self.pet_repository.get_by_id(command.pet_id)
            if not pet:
                raise PetNotFoundError(command.pet_id)
            
            # 验证当前用户是否是宠物的主人
            if pet.owner_id != command.current_user_id:
                from domain.pets.exceptions import UnauthorizedPetAccessError
                raise UnauthorizedPetAccessError("Only the current owner can transfer ownership")
            
            # 验证新主人是否存在
            new_owner = await self.user_repository.get_by_id(command.new_owner_id)
            if not new_owner:
                raise UserNotFoundError(f"New owner with id '{command.new_owner_id}' not found")
            
            # 验证不能转移给自己
            if pet.owner_id == command.new_owner_id:
                from domain.pets.exceptions import InvalidOwnershipTransferError
                raise InvalidOwnershipTransferError("Cannot transfer pet to the same owner")
            
            # 执行转移
            pet.change_owner(command.new_owner_id)
            
            # 保存更新
            return await self.pet_repository.update(pet)


class UpdatePetHandler:
    """更新宠物命令处理器"""
    
    def __init__(
        self,
        pet_repository: PetRepository,
        breed_repository: BreedRepository,
        pet_domain_service: PetDomainService = None,
    ):
        self.pet_repository = pet_repository
        self.breed_repository = breed_repository
        self.pet_domain_service = pet_domain_service
        self.logger = logger
    
    async def handle(self, command: UpdatePetCommand) -> Pet:
        """处理更新宠物命令"""
        # 获取现有宠物
        pet = await self.pet_repository.get_by_id(command.pet_id)
        if not pet:
            raise PetNotFoundError(command.pet_id)

        # 检查宠物名唯一性
        if command.name and command.name != pet.name:
            if await self.pet_repository.exists_by_name(command.name, exclude_id=pet.id):
                raise DuplicatePetNameError(f"Pet name '{command.name}' already exists")

        if command.name is not None:
            pet.name = command.name
        if command.breed_id is not None:
            # 验证品种存在
            breed = await self.breed_repository.get_by_id(command.breed_id)
            if not breed:
                raise BreedNotFoundError(f"Breed with id '{command.breed_id}' not found")
            pet.breed_id = command.breed_id
        if command.birth_date is not None:
            pet.birth_date = command.birth_date
        if command.gender is not None:
            pet.gender = command.gender
        if command.morphology_id is not None and self.pet_domain_service:
            # 如果有领域服务，使用领域服务更新形态学（包含兼容性验证）
            await self.pet_domain_service.update_pet_morphology(
                pet_id=pet.id,
                morphology_id=command.morphology_id,
                current_user_id=command.owner_id or pet.owner_id,
            )
        elif command.morphology_id is not None:
            # 如果没有领域服务，直接更新形态学
            pet.update_morphology(command.morphology_id)

        # 更新时间戳
        pet._update_timestamp()

        # 保存更新
        return await self.pet_repository.update(pet)


class DeletePetHandler:
    """删除宠物命令处理器"""
    
    def __init__(self, pet_repository: PetRepository):
        self.pet_repository = pet_repository
        self.logger = logger
    
    async def handle(self, command: DeletePetCommand) -> bool:
        """处理删除宠物命令"""
        # 检查宠物是否存在
        pet = await self.pet_repository.get_by_id(command.pet_id)
        if not pet:
            raise PetNotFoundError(command.pet_id)

        # 执行软删除
        return await self.pet_repository.delete(command.pet_id)
