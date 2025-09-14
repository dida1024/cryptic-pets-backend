"""
品种查询处理器
实现CQRS模式的查询部分
"""

from loguru import logger

from application.breeds.queries import (
    GetBreedByIdQuery,
    GetBreedByNameQuery,
    ListBreedsQuery,
    SearchBreedsQuery,
)
from application.breeds.view_models import (
    BreedDetailsView,
    BreedSearchResult,
    BreedSummaryView,
    BreedWithPetsView,
)
from domain.pets.exceptions import BreedNotFoundError
from domain.pets.repository import BreedRepository, PetRepository


class BreedQueryService:
    """品种查询服务 - 专门处理读操作"""

    def __init__(
        self,
        breed_repository: BreedRepository,
        pet_repository: PetRepository | None = None,
    ):
        self.breed_repository = breed_repository
        self.pet_repository = pet_repository
        self.logger = logger

    async def get_breed_details(self, query: GetBreedByIdQuery) -> BreedDetailsView:
        """获取品种详情"""
        # 获取品种
        breed = await self.breed_repository.get_by_id(query.breed_id)
        if not breed:
            raise BreedNotFoundError(query.breed_id)

        # 创建详情视图
        breed_view = BreedDetailsView.from_entity(breed)

        return breed_view

    async def get_breed_by_name(self, query: GetBreedByNameQuery) -> BreedDetailsView:
        """根据名称获取品种"""
        # 获取品种
        breed = await self.breed_repository.get_by_name(query.name, language=query.language)
        if not breed:
            raise BreedNotFoundError(f"Breed with name '{query.name}' not found")

        # 创建详情查询
        detail_query = GetBreedByIdQuery(
            breed_id=breed.id,
            include_pets=query.include_pets,
        )

        # 使用详情查询处理器
        return await self.get_breed_details(detail_query)

    async def search_breeds(self, query: SearchBreedsQuery) -> BreedSearchResult:
        """搜索品种"""
        # 搜索品种
        breeds, total_count = await self.breed_repository.search_breeds(
            search_term=query.search_term,
            language=query.language,
            page=query.page,
            page_size=query.page_size,
            include_deleted=query.include_deleted,
        )

        # 创建摘要视图模型
        breed_views = [BreedSummaryView.from_entity(breed) for breed in breeds]

        # 创建搜索结果
        return BreedSearchResult.create(
            breeds=breed_views,
            total=total_count,
            page=query.page,
            page_size=query.page_size,
        )

    async def list_breeds(self, query: ListBreedsQuery) -> BreedSearchResult:
        """获取品种列表（保持向后兼容）"""
        # 获取品种列表
        breeds, total_count = await self.breed_repository.list_all(
            page=query.page,
            page_size=query.page_size,
            include_deleted=query.include_deleted,
        )

        # 创建摘要视图模型
        breed_views = [BreedSummaryView.from_entity(breed) for breed in breeds]

        # 创建搜索结果
        return BreedSearchResult.create(
            breeds=breed_views,
            total=total_count,
            page=query.page,
            page_size=query.page_size,
        )

    async def get_breed_with_pets(self, query: GetBreedByIdQuery) -> BreedWithPetsView:
        """获取包含宠物信息的品种详情"""
        # 获取品种详情
        breed_details = await self.get_breed_details(query)

        # 获取宠物数量（如果有宠物仓储）
        pets_count = 0
        if self.pet_repository and query.include_pets:
            pets = await self.pet_repository.get_by_breed_id(query.breed_id)
            pets_count = len(pets)

        # 创建包含宠物信息的视图
        return BreedWithPetsView(
            breed=breed_details,
            pets_count=pets_count,
        )
