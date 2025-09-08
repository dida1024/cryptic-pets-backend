"""
宠物查询处理器
实现CQRS模式的查询部分
"""

from loguru import logger

from application.pets.queries import (
    GetPetByIdQuery,
    GetPetByNameQuery,
    ListPetsByBreedQuery,
    ListPetsByMorphologyQuery,
    ListPetsByOwnerQuery,
    SearchPetsQuery,
)
from application.pets.view_models import (
    BreedView,
    MorphologyView,
    OwnerView,
    PetDetailsView,
    PetSearchResult,
    PetSummaryView,
)
from domain.pets.exceptions import PetNotFoundError
from domain.pets.repository import BreedRepository, MorphologyRepository, PetRepository
from domain.users.repository import UserRepository


class PetQueryService:
    """宠物查询服务 - 专门处理读操作"""

    def __init__(
        self,
        pet_repository: PetRepository,
        user_repository: UserRepository,
        breed_repository: BreedRepository,
        morphology_repository: MorphologyRepository,
    ):
        self.pet_repository = pet_repository
        self.user_repository = user_repository
        self.breed_repository = breed_repository
        self.morphology_repository = morphology_repository
        self.logger = logger

    async def get_pet_details(self, query: GetPetByIdQuery) -> PetDetailsView:
        """获取宠物详情"""
        # 获取宠物
        pet = await self.pet_repository.get_by_id(query.pet_id)
        if not pet:
            raise PetNotFoundError(query.pet_id)

        # 创建基础视图模型
        pet_view = PetDetailsView(
            id=pet.id,
            name=pet.name,
            description=pet.description,
            birth_date=pet.birth_date,
            gender=pet.gender,
            created_at=pet.created_at,
            updated_at=pet.updated_at,
        )

        # 加载主人信息（如果请求）
        if query.include_owner:
            owner = await self.user_repository.get_by_id(pet.owner_id)
            if owner:
                pet_view.owner = OwnerView(
                    id=owner.id,
                    username=owner.username,
                    full_name=owner.full_name,
                )

        # 加载品种信息（如果请求）
        if query.include_breed:
            breed = await self.breed_repository.get_by_id(pet.breed_id)
            if breed:
                pet_view.breed = BreedView.from_entity(breed)

        # 加载形态学信息（如果请求）
        if query.include_morphology and pet.morphology_id:
            morphology = await self.morphology_repository.get_by_id(pet.morphology_id)
            if morphology:
                pet_view.morphology = MorphologyView.from_entity(morphology)

        # 加载图片信息
        # 在实际实现中，这里应该加载宠物的图片
        # 简化起见，这里不实现

        return pet_view

    async def get_pet_by_name(self, query: GetPetByNameQuery) -> PetDetailsView:
        """根据名称获取宠物"""
        # 获取宠物
        pet = await self.pet_repository.get_by_name(query.name, language=query.language)
        if not pet:
            raise PetNotFoundError(f"Pet with name '{query.name}' not found")

        # 创建详情查询
        detail_query = GetPetByIdQuery(
            pet_id=pet.id,
            include_owner=True,
            include_breed=True,
            include_morphology=True,
        )

        # 使用详情查询处理器
        return await self.get_pet_details(detail_query)

    async def search_pets(self, query: SearchPetsQuery) -> PetSearchResult:
        """搜索宠物"""
        # 搜索宠物
        pets, total_count = await self.pet_repository.search_pets(
            search_term=query.search_term,
            owner_id=query.owner_id,
            breed_id=query.breed_id,
            morphology_id=query.morphology_id,
            page=query.page,
            page_size=query.page_size,
            include_deleted=query.include_deleted,
        )

        # 创建摘要视图模型
        pet_views = []
        for pet in pets:
            # 获取主人名称（如果有主人ID）
            owner_name = None
            if pet.owner_id:
                owner = await self.user_repository.get_by_id(pet.owner_id)
                if owner:
                    owner_name = owner.username or owner.full_name

            # 获取品种名称（如果有品种ID）
            breed_name = None
            if pet.breed_id:
                breed = await self.breed_repository.get_by_id(pet.breed_id)
                if breed and breed.name:
                    # 尝试获取当前语言的名称，默认为英语
                    breed_name = breed.name

            # 创建摘要视图
            pet_view = PetSummaryView(
                id=pet.id,
                name=pet.name,
                gender=pet.gender,
                created_at=pet.created_at,
                owner_name=owner_name,
                breed_name=breed_name,
                # 在实际实现中，这里应该获取主图URL
                primary_picture_url=None,
            )
            pet_views.append(pet_view)

        # 创建搜索结果
        return PetSearchResult.create(
            pets=pet_views,
            total=total_count,
            page=query.page,
            page_size=query.page_size,
        )

    async def list_pets_by_owner(self, query: ListPetsByOwnerQuery) -> PetSearchResult:
        """列出用户的宠物"""
        # 验证用户存在
        owner = await self.user_repository.get_by_id(query.owner_id)
        if not owner:
            from domain.users.exceptions import UserNotFoundError
            raise UserNotFoundError(f"User with id '{query.owner_id}' not found")

        # 获取用户的宠物
        pets = await self.pet_repository.get_by_owner_id(query.owner_id)

        # 计算分页
        start_idx = (query.page - 1) * query.page_size
        end_idx = start_idx + query.page_size
        paginated_pets = pets[start_idx:end_idx]

        # 创建摘要视图模型
        pet_views = []
        for pet in paginated_pets:
            # 获取品种名称（如果有品种ID）
            breed_name = None
            if pet.breed_id:
                breed = await self.breed_repository.get_by_id(pet.breed_id)
                if breed and breed.name:
                    # 尝试获取当前语言的名称，默认为英语
                    breed_name = breed.name.get("en", "")

            # 创建摘要视图
            pet_view = PetSummaryView(
                id=pet.id,
                name=pet.name,
                gender=pet.gender,
                created_at=pet.created_at,
                owner_name=owner.username or owner.full_name,
                breed_name=breed_name,
                # 在实际实现中，这里应该获取主图URL
                primary_picture_url=None,
            )
            pet_views.append(pet_view)

        # 创建搜索结果
        return PetSearchResult.create(
            pets=pet_views,
            total=len(pets),
            page=query.page,
            page_size=query.page_size,
        )

    async def list_pets_by_breed(self, query: ListPetsByBreedQuery) -> PetSearchResult:
        """列出特定品种的宠物"""
        # 验证品种存在
        breed = await self.breed_repository.get_by_id(query.breed_id)
        if not breed:
            from domain.pets.exceptions import BreedNotFoundError
            raise BreedNotFoundError(query.breed_id)

        # 获取该品种的宠物
        pets = await self.pet_repository.get_by_breed_id(query.breed_id)

        # 计算分页
        start_idx = (query.page - 1) * query.page_size
        end_idx = start_idx + query.page_size
        paginated_pets = pets[start_idx:end_idx]

        # 创建摘要视图模型
        pet_views = []
        for pet in paginated_pets:
            # 获取主人名称（如果有主人ID）
            owner_name = None
            if pet.owner_id:
                owner = await self.user_repository.get_by_id(pet.owner_id)
                if owner:
                    owner_name = owner.username or owner.full_name

            # 创建摘要视图
            pet_view = PetSummaryView(
                id=pet.id,
                name=pet.name,
                gender=pet.gender,
                created_at=pet.created_at,
                owner_name=owner_name,
                breed_name=breed.name.get("en", "") if breed.name else None,
                # 在实际实现中，这里应该获取主图URL
                primary_picture_url=None,
            )
            pet_views.append(pet_view)

        # 创建搜索结果
        return PetSearchResult.create(
            pets=pet_views,
            total=len(pets),
            page=query.page,
            page_size=query.page_size,
        )

    async def list_pets_by_morphology(self, query: ListPetsByMorphologyQuery) -> PetSearchResult:
        """列出特定形态学的宠物"""
        # 验证形态学存在
        morphology = await self.morphology_repository.get_by_id(query.morphology_id)
        if not morphology:
            from domain.pets.exceptions import MorphologyNotFoundError
            raise MorphologyNotFoundError(query.morphology_id)

        # 获取该形态学的宠物
        pets = await self.pet_repository.get_by_morphology_id(query.morphology_id)

        # 计算分页
        start_idx = (query.page - 1) * query.page_size
        end_idx = start_idx + query.page_size
        paginated_pets = pets[start_idx:end_idx]

        # 创建摘要视图模型
        pet_views = []
        for pet in paginated_pets:
            # 获取主人名称（如果有主人ID）
            owner_name = None
            if pet.owner_id:
                owner = await self.user_repository.get_by_id(pet.owner_id)
                if owner:
                    owner_name = owner.username or owner.full_name

            # 获取品种名称（如果有品种ID）
            breed_name = None
            if pet.breed_id:
                breed = await self.breed_repository.get_by_id(pet.breed_id)
                if breed and breed.name:
                    # 尝试获取当前语言的名称，默认为英语
                    breed_name = breed.name.get("en", "")

            # 创建摘要视图
            pet_view = PetSummaryView(
                id=pet.id,
                name=pet.name,
                gender=pet.gender,
                created_at=pet.created_at,
                owner_name=owner_name,
                breed_name=breed_name,
                # 在实际实现中，这里应该获取主图URL
                primary_picture_url=None,
            )
            pet_views.append(pet_view)

        # 创建搜索结果
        return PetSearchResult.create(
            pets=pet_views,
            total=len(pets),
            page=query.page,
            page_size=query.page_size,
        )
