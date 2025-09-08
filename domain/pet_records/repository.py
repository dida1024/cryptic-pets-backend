from abc import abstractmethod

from domain.common.repository import BaseRepository
from domain.pet_records.entities import PetRecord


class PetRecordRepository(BaseRepository[PetRecord]):
    """用户仓储接口"""

    @abstractmethod
    async def get_by_username(self, username: str) -> PetRecord | None:
        """根据用户名获取记录"""
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> PetRecord | None:
        """根据ID获取记录"""
        pass

    @abstractmethod
    async def create(self, user: PetRecord) -> PetRecord:
        """创建记录"""
        pass

    @abstractmethod
    async def update(self, user: PetRecord) -> PetRecord:
        """更新记录"""
        pass

    @abstractmethod
    async def list_all(
        self,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None,
        record_type: str | None = None,
        is_active: bool | None = None,
        include_deleted: bool = False,
    ) -> tuple[list[PetRecord], int]:
        """
        获取记录列表

        Returns:
            tuple[List[PetRecord], int]: (记录列表, 总数量)
        """
        pass
