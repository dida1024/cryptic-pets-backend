from abc import abstractmethod

from domain.common.repository import BaseRepository
from domain.pets.entities import Breed, Gene, Morphology, Pet
from domain.pets.value_objects import GeneCategoryEnum, InheritanceTypeEnum


class PetRepository(BaseRepository[Pet]):
    """宠物聚合Repository接口"""

    @abstractmethod
    async def get_by_owner_id(self, owner_id: str) -> list[Pet]:
        """根据主人ID获取宠物列表"""
        pass

    @abstractmethod
    async def get_by_breed_id(self, breed_id: str) -> list[Pet]:
        """根据品种ID获取宠物列表"""
        pass

    @abstractmethod
    async def get_by_morphology_id(self, morphology_id: str) -> list[Pet]:
        """根据形态学ID获取宠物列表"""
        pass

    @abstractmethod
    async def get_by_name(self, name: str, language: str = "en") -> Pet | None:
        """根据名称获取宠物（支持国际化）"""
        pass

    @abstractmethod
    async def exists_by_name(self, name: str, exclude_id: str | None = None) -> bool:
        """检查指定名称的宠物是否存在（可选排除ID）"""
        pass

    @abstractmethod
    async def search_pets(
        self,
        search_term: str,
        owner_id: str = None,
        breed_id: str = None,
        morphology_id: str = None,
        page: int = 1,
        page_size: int = 10,
        include_deleted: bool = False,
    ) -> tuple[list[Pet], int]:
        """
        搜索宠物

        Args:
            search_term: 搜索关键词
            owner_id: 可选的主人ID过滤
            breed_id: 可选的品种ID过滤
            morphology_id: 可选的形态学ID过滤
            page: 页码，从1开始
            page_size: 每页大小
            include_deleted: 是否包含已删除的记录

        Returns:
            tuple[List[Pet], int]: (宠物列表, 总数量)
        """
        pass


class BreedRepository(BaseRepository[Breed]):
    """品种聚合Repository接口"""

    @abstractmethod
    async def get_by_name(self, name: str, language: str = "en") -> Breed | None:
        """根据名称获取品种（支持国际化）"""
        pass

    @abstractmethod
    async def search_breeds(
        self,
        search_term: str,
        language: str = "en",
        page: int = 1,
        page_size: int = 10,
        include_deleted: bool = False,
    ) -> tuple[list[Breed], int]:
        """
        搜索品种

        Args:
            search_term: 搜索关键词
            language: 搜索语言
            page: 页码，从1开始
            page_size: 每页大小
            include_deleted: 是否包含已删除的记录

        Returns:
            tuple[List[Breed], int]: (品种列表, 总数量)
        """
        pass


class GeneRepository(BaseRepository[Gene]):
    """基因聚合Repository接口"""

    @abstractmethod
    async def get_by_category(self, category: GeneCategoryEnum) -> list[Gene]:
        """根据基因类别获取基因列表"""
        pass

    @abstractmethod
    async def get_by_inheritance_type(self, inheritance_type: InheritanceTypeEnum) -> list[Gene]:
        """根据遗传类型获取基因列表"""
        pass

    @abstractmethod
    async def get_by_notation(self, notation: str) -> Gene | None:
        """根据基因标记获取基因"""
        pass

    @abstractmethod
    async def search_genes(
        self,
        search_term: str,
        category: GeneCategoryEnum | None = None,
        inheritance_type: InheritanceTypeEnum | None = None,
        language: str = "en",
        page: int = 1,
        page_size: int = 10,
        include_deleted: bool = False,
    ) -> tuple[list[Gene], int]:
        """
        搜索基因

        Args:
            search_term: 搜索关键词
            category: 可选的基因类别过滤
            inheritance_type: 可选的遗传类型过滤
            language: 搜索语言
            page: 页码，从1开始
            page_size: 每页大小
            include_deleted: 是否包含已删除的记录

        Returns:
            tuple[List[Gene], int]: (基因列表, 总数量)
        """
        pass


class MorphologyRepository(BaseRepository[Morphology]):
    """形态学聚合Repository接口"""

    @abstractmethod
    async def get_by_gene_combination(self, gene_ids: list[str]) -> list[Morphology]:
        """根据基因组合获取形态学列表"""
        pass

    @abstractmethod
    async def get_by_required_genes(self, gene_ids: list[str]) -> list[Morphology]:
        """根据必需基因获取形态学列表"""
        pass

    @abstractmethod
    async def get_morphologies_containing_gene(self, gene_id: str) -> list[Morphology]:
        """获取包含指定基因的所有形态学"""
        pass

    @abstractmethod
    async def is_compatible_with_breed(self, morphology_id: str, breed_id: str) -> bool:
        """检查形态学是否与品种兼容"""
        pass

    @abstractmethod
    async def search_morphologies(
        self,
        search_term: str,
        gene_ids: list[str] | None = None,
        language: str = "en",
        page: int = 1,
        page_size: int = 10,
        include_deleted: bool = False,
    ) -> tuple[list[Morphology], int]:
        """
        搜索形态学

        Args:
            search_term: 搜索关键词
            gene_ids: 可选的基因ID列表过滤
            language: 搜索语言
            page: 页码，从1开始
            page_size: 每页大小
            include_deleted: 是否包含已删除的记录

        Returns:
            tuple[List[Morphology], int]: (形态学列表, 总数量)
        """
        pass
