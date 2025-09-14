"""
品种命令处理器
实现CQRS模式的命令部分，处理写操作
"""

from loguru import logger

from application.breeds.commands import (
    CreateBreedCommand,
    DeleteBreedCommand,
    UpdateBreedCommand,
)
from domain.pets.entities import Breed
from domain.pets.exceptions import BreedNotFoundError
from domain.pets.repository import BreedRepository


class CreateBreedHandler:
    """创建品种命令处理器"""

    def __init__(self, breed_repository: BreedRepository):
        self.breed_repository = breed_repository
        self.logger = logger

    async def handle(self, command: CreateBreedCommand) -> Breed:
        """处理创建品种命令"""
        # 创建品种实体
        breed = Breed(
            name=command.name,
            description=command.description,
        )

        self.logger.info(f"Creating breed: {breed.name}")

        # 保存品种
        created_breed = await self.breed_repository.create(breed)

        # 添加领域事件
        from domain.pets.events import BreedCreatedEvent
        created_breed._add_domain_event(BreedCreatedEvent(
            breed_id=created_breed.id,
            name=created_breed.name,
        ))

        return created_breed


class UpdateBreedHandler:
    """更新品种命令处理器"""

    def __init__(self, breed_repository: BreedRepository):
        self.breed_repository = breed_repository
        self.logger = logger

    async def handle(self, command: UpdateBreedCommand) -> Breed:
        """处理更新品种命令"""
        # 获取现有品种
        breed = await self.breed_repository.get_by_id(command.breed_id)
        if not breed:
            raise BreedNotFoundError(command.breed_id)

        # 更新字段
        if command.name is not None:
            breed.name = command.name
        if command.description is not None:
            breed.description = command.description

        # 更新时间戳
        breed._update_timestamp()

        self.logger.info(f"Updating breed: {breed.name}")

        # 保存更新
        updated_breed = await self.breed_repository.update(breed)

        # 添加领域事件
        from domain.pets.events import BreedUpdatedEvent
        updated_breed._add_domain_event(BreedUpdatedEvent(
            breed_id=updated_breed.id,
            name=updated_breed.name,
        ))

        return updated_breed


class DeleteBreedHandler:
    """删除品种命令处理器"""

    def __init__(self, breed_repository: BreedRepository):
        self.breed_repository = breed_repository
        self.logger = logger

    async def handle(self, command: DeleteBreedCommand) -> bool:
        """处理删除品种命令"""
        # 检查品种是否存在
        breed = await self.breed_repository.get_by_id(command.breed_id)
        if not breed:
            raise BreedNotFoundError(command.breed_id)

        self.logger.info(f"Deleting breed: {breed.name}")

        # 执行软删除
        result = await self.breed_repository.delete(command.breed_id)

        # 添加领域事件
        from domain.pets.events import BreedDeletedEvent
        breed._add_domain_event(BreedDeletedEvent(
            breed_id=breed.id,
            name=breed.name,
        ))

        return result
