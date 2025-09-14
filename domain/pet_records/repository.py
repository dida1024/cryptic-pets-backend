from abc import abstractmethod

from domain.common.repository import BaseRepository
from domain.pet_records.entities import PetRecord
from domain.pet_records.value_objects import PetEventTypeEnum


class PetRecordRepository(BaseRepository[PetRecord]):
    """宠物记录仓储接口"""

    @abstractmethod
    async def get_by_id(self, record_id: str) -> PetRecord | None:
        """根据ID获取记录"""
        pass

    @abstractmethod
    async def create(self, pet_record: PetRecord) -> PetRecord:
        """创建记录"""
        pass

    @abstractmethod
    async def update(self, pet_record: PetRecord) -> PetRecord:
        """更新记录"""
        pass

    @abstractmethod
    async def delete(self, record_id: str) -> bool:
        """删除记录（软删除）"""
        pass

    @abstractmethod
    async def list_all(
        self,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None,
        pet_id: str | None = None,
        event_type: PetEventTypeEnum | None = None,
        creator_id: str | None = None,
        include_deleted: bool = False,
    ) -> tuple[list[PetRecord], int]:
        """
        获取记录列表

        Returns:
            tuple[List[PetRecord], int]: (记录列表, 总数量)
        """
        pass

    @abstractmethod
    async def get_by_pet_id(self, pet_id: str) -> list[PetRecord]:
        """根据宠物ID获取记录列表"""
        pass

    @abstractmethod
    async def get_by_creator_id(self, creator_id: str) -> list[PetRecord]:
        """根据创建者ID获取记录列表"""
        pass

    @abstractmethod
    async def search_pet_records(
        self,
        search_term: str | None = None,
        pet_id: str | None = None,
        event_type: PetEventTypeEnum | None = None,
        creator_id: str | None = None,
        page: int = 1,
        page_size: int = 10,
        include_deleted: bool = False,
    ) -> tuple[list[PetRecord], int]:
        """搜索宠物记录"""
        pass
