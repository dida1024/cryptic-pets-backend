"""
宠物记录查询处理器
实现CQRS模式的查询部分
"""

from loguru import logger

from application.pet_records.queries import (
    GetPetRecordByIdQuery,
    ListPetRecordsQuery,
    SearchPetRecordsQuery,
)
from application.pet_records.view_models import (
    PetRecordDetailsView,
    PetRecordSearchResult,
    PetRecordSummaryView,
)
from domain.pet_records.exceptions import PetRecordNotFoundError
from domain.pet_records.repository import PetRecordRepository


class PetRecordQueryService:
    """宠物记录查询服务 - 专门处理读操作"""

    def __init__(self, pet_record_repository: PetRecordRepository):
        self.pet_record_repository = pet_record_repository
        self.logger = logger

    async def get_pet_record_details(self, query: GetPetRecordByIdQuery) -> PetRecordDetailsView:
        """获取宠物记录详情"""
        # 获取记录
        pet_record = await self.pet_record_repository.get_by_id(query.pet_record_id)
        if not pet_record:
            raise PetRecordNotFoundError(query.pet_record_id)

        # 创建详情视图
        record_view = PetRecordDetailsView.from_entity(pet_record)
        return record_view

    async def search_pet_records(self, query: SearchPetRecordsQuery) -> PetRecordSearchResult:
        """搜索宠物记录"""
        # 搜索记录
        records, total_count = await self.pet_record_repository.search_pet_records(
            search_term=query.search_term,
            pet_id=query.pet_id,
            event_type=query.event_type,
            creator_id=query.creator_id,
            page=query.page,
            page_size=query.page_size,
            include_deleted=query.include_deleted,
        )

        # 创建摘要视图模型
        record_views = [PetRecordSummaryView.from_entity(record) for record in records]

        # 创建搜索结果
        return PetRecordSearchResult.create(
            records=record_views,
            total=total_count,
            page=query.page,
            page_size=query.page_size,
        )

    async def list_pet_records(self, query: ListPetRecordsQuery) -> PetRecordSearchResult:
        """获取宠物记录列表"""
        # 获取记录列表
        records, total_count = await self.pet_record_repository.list_all(
            page=query.page,
            page_size=query.page_size,
            search=query.search,
            pet_id=query.pet_id,
            event_type=query.event_type,
            creator_id=query.creator_id,
            include_deleted=query.include_deleted,
        )

        # 创建摘要视图模型
        record_views = [PetRecordSummaryView.from_entity(record) for record in records]

        # 创建搜索结果
        return PetRecordSearchResult.create(
            records=record_views,
            total=total_count,
            page=query.page,
            page_size=query.page_size,
        )

    async def get_pet_records_by_pet_id(self, pet_id: str) -> list[PetRecordSummaryView]:
        """根据宠物ID获取记录列表"""
        records = await self.pet_record_repository.get_by_pet_id(pet_id)
        return [PetRecordSummaryView.from_entity(record) for record in records]

    async def get_pet_records_by_creator_id(self, creator_id: str) -> list[PetRecordSummaryView]:
        """根据创建者ID获取记录列表"""
        records = await self.pet_record_repository.get_by_creator_id(creator_id)
        return [PetRecordSummaryView.from_entity(record) for record in records]
