from abc import abstractmethod

from domain.common.repository import BaseRepository
from domain.users.entities import User


class UserRepository(BaseRepository[User]):
    """用户仓储接口"""

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        """根据用户名获取用户"""
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> User | None:
        """根据ID获取用户"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """根据邮箱获取用户"""
        pass

    @abstractmethod
    async def create(self, user: User) -> User:
        """创建用户"""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """更新用户"""
        pass

    @abstractmethod
    async def list_all(
        self,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None,
        user_type: str | None = None,
        is_active: bool | None = None,
        include_deleted: bool = False,
    ) -> tuple[list[User], int]:
        """
        获取用户列表

        Returns:
            tuple[List[User], int]: (用户列表, 总数量)
        """
        pass

    @abstractmethod
    async def exists_by_username(self, username: str, exclude_id: str | None = None) -> bool:
        """检查用户名是否存在"""
        pass

    @abstractmethod
    async def exists_by_email(self, email: str, exclude_id: str | None = None) -> bool:
        """检查邮箱是否存在"""
        pass
