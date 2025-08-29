from application.breeds.commands import (
    CreateBreedCommand,
    DeleteBreedCommand,
    ListBreedsQuery,
    SearchBreedsQuery,
    UpdateBreedCommand,
)
from domain.pets.entities import Breed
from domain.pets.exceptions import BreedNotFoundError
from domain.pets.repository import BreedRepository


class BreedService:
    """品种服务"""

    def __init__(self, breed_repository: BreedRepository):
        self.breed_repository = breed_repository

    async def create_breed(self, command: CreateBreedCommand) -> Breed:
        breed = Breed(name=command.name, description=command.description)
        return await self.breed_repository.create(breed)

    async def get_breed_by_id(self, breed_id: str) -> Breed:
        breed = await self.breed_repository.get_by_id(breed_id)
        if not breed:
            raise BreedNotFoundError(breed_id)
        return breed

    async def update_breed(self, command: UpdateBreedCommand) -> Breed:
        breed = await self.get_breed_by_id(command.breed_id)
        if command.name is not None:
            breed.name = command.name
        if command.description is not None:
            breed.description = command.description
        breed._update_timestamp()
        return await self.breed_repository.update(breed)

    async def delete_breed(self, command: DeleteBreedCommand) -> bool:
        # 存在性校验
        _ = await self.get_breed_by_id(command.breed_id)
        return await self.breed_repository.delete(command.breed_id)

    async def list_all(self, query: ListBreedsQuery) -> tuple[list[Breed], int]:
        return await self.breed_repository.list_all(
            page=query.page,
            page_size=query.page_size,
            include_deleted=query.include_deleted,
        )

    async def search(self, query: SearchBreedsQuery) -> tuple[list[Breed], int]:
        return await self.breed_repository.search_breeds(
            search_term=query.search,
            language=query.language,
            page=query.page,
            page_size=query.page_size,
            include_deleted=query.include_deleted,
        )


