"""
仓储基础设施
提供仓储模式的基础类和规约支持
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from domain.common.specifications import Specification

T = TypeVar('T')


class SpecificationRepository(Generic[T], ABC):
    """支持规约模式的仓储基类"""

    @abstractmethod
    async def find_by_specification(
        self,
        specification: Specification[T],
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[T], int]:
        """
        根据规约查找实体

        Args:
            specification: 用于筛选的规约
            page: 页码，从1开始
            page_size: 每页大小

        Returns:
            tuple[list[T], int]: (实体列表, 总数量)
        """
        pass

    @abstractmethod
    async def count_by_specification(self, specification: Specification[T]) -> int:
        """
        根据规约计算实体数量

        Args:
            specification: 用于筛选的规约

        Returns:
            int: 符合规约的实体数量
        """
        pass

    @abstractmethod
    async def exists_by_specification(self, specification: Specification[T]) -> bool:
        """
        检查是否存在符合规约的实体

        Args:
            specification: 用于筛选的规约

        Returns:
            bool: 是否存在符合规约的实体
        """
        pass

    @abstractmethod
    async def find_one_by_specification(self, specification: Specification[T]) -> T | None:
        """
        根据规约查找单个实体

        Args:
            specification: 用于筛选的规约

        Returns:
            T | None: 符合规约的实体，如果不存在则返回None
        """
        pass
