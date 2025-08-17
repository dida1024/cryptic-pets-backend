from abc import ABC, abstractmethod

from domain.pets.entities import Pet


class PetRepository(ABC):
    """宠物仓储接口"""

    @abstractmethod
    async def get_by_id(self, pet_id: str) -> Pet | None:
        """根据ID获取宠物"""
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Pet | None:
        """根据名称获取宠物"""
        pass

    @abstractmethod
    async def create(self, pet: Pet) -> Pet:
        """创建宠物"""
        pass

    @abstractmethod
    async def update(self, pet: Pet) -> Pet:
        """更新宠物"""
        pass

    @abstractmethod
    async def delete(self, pet_id: str) -> bool:
        """删除宠物（软删除）"""
        pass

    @abstractmethod
    async def list_pets(
        self,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None,
        include_deleted: bool = False,
    ) -> tuple[list[Pet], int]:
        """
        获取用户列表

        Returns:
            tuple[List[Pet], int]: (宠物列表, 总数量)
        """
        pass
