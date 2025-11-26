from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar('T')


class BaseRepository[T](ABC):
    """基础Repository接口，定义通用CRUD操作"""

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> T | None:
        """根据ID获取实体"""
        pass

    @abstractmethod
    async def create(self, entity: T) -> T:
        """创建实体"""
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """更新实体"""
        pass

    @abstractmethod
    async def delete(self, entity: T | str) -> bool:
        """删除实体（软删除）。可以直接传递实体或实体ID。"""
        pass

    @abstractmethod
    async def list_all(
        self,
        page: int = 1,
        page_size: int = 10,
        include_deleted: bool = False
    ) -> tuple[list[T], int]:
        """
        获取实体列表

        Args:
            page: 页码，从1开始
            page_size: 每页大小
            include_deleted: 是否包含已删除的记录

        Returns:
            tuple[List[T], int]: (实体列表, 总数量)
        """
        pass
