from loguru import logger
from application.pets.commands import (
    CreatePetCommand,
    DeletePetCommand,
    ListPetsQuery,
    UpdatePetCommand,
)
from domain.pets.entities import Breed, Pet
from domain.pets.exceptions import BreedNotFoundError, PetNotFoundError
from domain.pets.repository import BreedRepository, PetRepository
from domain.users.exceptions import UserNotFoundError
from domain.users.repository import UserRepository


class PetService:
    """宠物服务"""

    def __init__(self, pet_repository: PetRepository, user_repository: UserRepository, breed_repository: BreedRepository):
        self.pet_repository = pet_repository
        self.user_repository = user_repository
        self.breed_repository = breed_repository

    async def create_pet(self, command: CreatePetCommand) -> Pet:
        """创建宠物"""
        # 检查宠物名是否已存在
        if await self.pet_repository.exists_by_name(command.name):
            from domain.pets.exceptions import DuplicatePetNameError
            raise DuplicatePetNameError(f"Pet name '{command.name}' already exists")

        # 装配领域实体（简化：直接用ID占位，真实系统应查询并装配）
        owner = await self.user_repository.get_by_id(command.owner_id)
        if not owner:
            raise UserNotFoundError(f"User with id '{command.owner_id}' not found")
        breed = await self.breed_repository.get_by_id(command.breed_id)
        if not breed:
            raise BreedNotFoundError(f"Breed with id '{command.breed_id}' not found")
        pet = Pet(
            name=command.name,
            description=command.description,
            owner=owner,
            breed=breed,
            birth_date=command.birth_date,
            gender=command.gender,
        )
        logger.info(f"Creating pet: {pet}")

        # 保存宠物
        return await self.pet_repository.create(pet)

    async def get_pet_by_id(self, pet_id: str) -> Pet:
        """根据ID获取宠物"""
        pet = await self.pet_repository.get_by_id(pet_id)
        if not pet:
            raise PetNotFoundError(f"Pet with id '{pet_id}' not found")
        return pet

    async def get_pet_by_name(self, name: str) -> Pet:
        """根据宠物名获取宠物"""
        pet = await self.pet_repository.get_by_name(name)
        if not pet:
            raise PetNotFoundError(f"Pet with name '{name}' not found")
        return pet



    async def update_pet(self, command: UpdatePetCommand) -> Pet:
        """更新宠物"""
        # 获取现有宠物
        pet = await self.get_pet_by_id(command.pet_id)

        # 检查宠物名唯一性
        if command.name and command.name != pet.name:
            if await self.pet_repository.exists_by_name(command.name, exclude_id=pet.id):
                from domain.pets.exceptions import DuplicatePetNameError
                raise DuplicatePetNameError(f"Pet name '{command.name}' already exists")

        if command.name is not None:
            pet.name = command.name
        if command.breed_id is not None:
            pet.breed = Breed(id=command.breed_id, name=None, description=None)
        if command.birth_date is not None:
            pet.birth_date = command.birth_date
        if command.gender is not None:
            pet.gender = command.gender

        # 更新时间戳
        pet._update_timestamp()

        # 保存更新
        return await self.pet_repository.update(pet)


    async def delete_pet(self, command: DeletePetCommand) -> bool:
        """删除宠物（软删除）"""
        # 检查宠物是否存在
        pet = await self.pet_repository.get_by_id(command.pet_id)
        if not pet:
            raise PetNotFoundError(f"Pet with id '{command.pet_id}' not found")

        # 执行软删除
        return await self.pet_repository.delete(command.pet_id)

    async def list_all(self, query: ListPetsQuery) -> tuple[list[Pet], int]:
        """获取宠物列表"""
        return await self.pet_repository.list_all(
            page=query.page,
            page_size=query.page_size,
            search=query.search,
            owner_id=query.owner_id,
        )
