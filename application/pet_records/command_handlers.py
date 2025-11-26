"""
宠物记录命令处理器
实现CQRS模式的命令部分，处理写操作
"""

from uuid import uuid4

from loguru import logger

from application.pet_records.commands import (
    CreatePetRecordCommand,
    DeletePetRecordCommand,
    UpdatePetRecordCommand,
)
from domain.pet_records.entities import PetRecord
from domain.pet_records.exceptions import PetRecordNotFoundError
from domain.pet_records.pet_record_data import PetRecordDataFactory
from domain.pet_records.repository import PetRecordRepository


class CreatePetRecordHandler:
    """创建宠物事件记录命令处理器"""

    def __init__(self, pet_record_repository: PetRecordRepository):
        self.pet_record_repository = pet_record_repository
        self.logger = logger

    async def handle(self, command: CreatePetRecordCommand) -> PetRecord:
        """处理创建宠物事件记录命令"""
        try:
            # 创建事件数据
            event_data = PetRecordDataFactory.create_data(
                event_type=command.event_type,
                **command.event_data
            )

            # 创建宠物记录实体
            pet_record = PetRecord(
                id=str(uuid4()),
                pet_id=command.pet_id,
                creator_id=command.creator_id,
                event_type=command.event_type,
                event_data=event_data,
            )

            # 保存到数据库
            # 添加领域事件
            from domain.pet_records.events import PetRecordCreatedEvent
            pet_record._add_domain_event(PetRecordCreatedEvent(
                record_id=pet_record.id,
                pet_id=pet_record.pet_id,
                event_type=pet_record.event_type,
            ))

            created_record = await self.pet_record_repository.create(pet_record)

            self.logger.info(f"Created pet record {created_record.id} for pet {command.pet_id}")
            return created_record

        except Exception as e:
            self.logger.error(f"Failed to create pet record: {e}")
            raise


class UpdatePetRecordHandler:
    """更新宠物事件记录命令处理器"""

    def __init__(self, pet_record_repository: PetRecordRepository):
        self.pet_record_repository = pet_record_repository
        self.logger = logger

    async def handle(self, command: UpdatePetRecordCommand) -> PetRecord:
        """处理更新宠物事件记录命令"""
        try:
            # 获取现有记录
            existing_record = await self.pet_record_repository.get_by_id(command.record_id)
            if not existing_record:
                raise PetRecordNotFoundError(command.record_id)

            # 更新字段
            if command.event_data is not None:
                # 重新创建事件数据
                event_data = PetRecordDataFactory.create_data(
                    event_type=existing_record.event_type,
                    **command.event_data
                )
                existing_record.event_data = event_data

            from domain.pet_records.events import PetRecordUpdatedEvent
            existing_record._add_domain_event(PetRecordUpdatedEvent(
                record_id=existing_record.id,
                pet_id=existing_record.pet_id,
                event_type=existing_record.event_type,
            ))

            # 保存更新
            updated_record = await self.pet_record_repository.update(existing_record)

            self.logger.info(f"Updated pet record {updated_record.id}")
            return updated_record

        except PetRecordNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to update pet record {command.record_id}: {e}")
            raise


class DeletePetRecordHandler:
    """删除宠物事件记录命令处理器"""

    def __init__(self, pet_record_repository: PetRecordRepository):
        self.pet_record_repository = pet_record_repository
        self.logger = logger

    async def handle(self, command: DeletePetRecordCommand) -> bool:
        """处理删除宠物事件记录命令"""
        try:
            # 检查记录是否存在
            existing_record = await self.pet_record_repository.get_by_id(command.record_id)
            if not existing_record:
                raise PetRecordNotFoundError(command.record_id)

            existing_record.mark_as_deleted()
            from domain.pet_records.events import PetRecordDeletedEvent
            existing_record._add_domain_event(PetRecordDeletedEvent(
                record_id=existing_record.id,
                pet_id=existing_record.pet_id,
                event_type=existing_record.event_type,
            ))

            if success := await self.pet_record_repository.delete(existing_record):
                self.logger.info(f"Deleted pet record {command.record_id}")
            else:
                self.logger.warning(f"Failed to delete pet record {command.record_id}")

            return success

        except PetRecordNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to delete pet record {command.record_id}: {e}")
            raise
