from loguru import logger
from sqlalchemy import ColumnElement, UnaryExpression, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domain.common.event_publisher import EventPublisher
from domain.pet_records.entities import PetRecord
from domain.pet_records.exceptions import PetRecordDomainError, PetRecordNotFoundError
from domain.pet_records.repository import PetRecordRepository
from domain.pet_records.value_objects import PetEventTypeEnum
from infrastructure.persistence.postgres.mappers.pet_record_mapper import (
    PetRecordMapper,
)
from infrastructure.persistence.postgres.models.pet_record import PetRecordModel
from infrastructure.persistence.postgres.repositories.event_aware_repository import (
    EventAwareRepository,
)


class PostgreSQLPetRecordRepositoryImpl(
    EventAwareRepository[PetRecord], PetRecordRepository
):
    """宠物记录Repository的PostgreSQL实现"""

    def __init__(
        self,
        session: AsyncSession,
        mapper: PetRecordMapper,
        event_publisher: EventPublisher,
    ):
        super().__init__(event_publisher)
        self.session = session
        self.mapper = mapper
        self.logger = logger

    async def get_by_id(self, record_id: str) -> PetRecord | None:
        """根据ID获取宠物记录"""
        try:
            stmt = (
                select(PetRecordModel)
                .options(
                    selectinload(PetRecordModel.pet),
                    selectinload(PetRecordModel.creator),
                )
                .where(PetRecordModel.id == record_id)
                .where(PetRecordModel.is_deleted.is_(False))
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self.mapper.to_domain(model)

        except Exception as e:
            self.logger.error(f"Failed to get pet record by id {record_id}: {e}")
            raise PetRecordDomainError(f"Failed to get pet record: {e}")

    async def create(self, pet_record: PetRecord) -> PetRecord:
        """创建宠物记录"""
        try:
            model = self.mapper.to_model(pet_record)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model, attribute_names=["pet", "creator"])

            # 发布领域事件并返回原实体
            await self._publish_events_from_entity(pet_record)
            return pet_record

        except Exception as e:
            self.logger.error(f"Failed to create pet record {pet_record.id}: {e}")
            raise PetRecordDomainError(f"Failed to create pet record: {e}")

    async def update(self, pet_record: PetRecord) -> PetRecord:
        """更新宠物记录"""
        try:
            existing_model = await self.session.get(PetRecordModel, pet_record.id)
            if existing_model is None or existing_model.is_deleted:
                raise PetRecordNotFoundError(pet_record.id)

            # 更新字段
            existing_model.pet_id = pet_record.pet_id
            existing_model.creator_id = pet_record.creator_id
            existing_model.event_type = pet_record.event_type
            existing_model.event_data = pet_record.event_data.model_dump()
            existing_model.updated_at = pet_record.updated_at

            await self.session.flush()
            await self.session.refresh(existing_model)

            await self._publish_events_from_entity(pet_record)
            return pet_record

        except PetRecordNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to update pet record {pet_record.id}: {e}")
            raise PetRecordDomainError(f"Failed to update pet record: {e}")

    async def delete(self, record: PetRecord | str) -> bool:
        """删除宠物记录（软删除）"""
        try:
            record_entity: PetRecord | None = record if isinstance(record, PetRecord) else None
            record_id = record.id if isinstance(record, PetRecord) else record

            model = await self.session.get(PetRecordModel, record_id)
            if model is None or model.is_deleted:
                return False

            if record_entity is None:
                record_entity = self.mapper.to_domain(model)

            model.is_deleted = True
            await self.session.flush()

            # 发布删除事件
            await self._publish_events_from_entity(record_entity)

            return True

        except Exception as e:
            self.logger.error(f"Failed to delete pet record {record_id}: {e}")
            raise PetRecordDomainError(f"Failed to delete pet record: {e}")

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
        """获取宠物记录列表"""
        try:
            stmt = select(
                PetRecordModel,
                func.count(PetRecordModel.id).over().label("total_count"),
            ).options(
                selectinload(PetRecordModel.pet),
                selectinload(PetRecordModel.creator),
            )
            conditions = self._generate_query_conditions(
                search, pet_id, event_type, creator_id, include_deleted
            )
            if conditions:
                stmt = stmt.where(*conditions)

            stmt = (
                stmt.offset((page - 1) * page_size)
                .limit(page_size)
                .order_by(PetRecordModel.created_at.desc())
            )

            result = await self.session.execute(stmt)
            rows = result.all()

            if not rows:
                return [], 0
            total_count = rows[0].total_count
            models = [row.PetRecordModel for row in rows]
            records = self.mapper.to_domain_list(models)
            return records, total_count

        except Exception as e:
            self.logger.error(f"Failed to list pet records: {e}")
            raise PetRecordDomainError(f"Failed to list pet records: {e}")

    async def get_by_pet_id(self, pet_id: str) -> list[PetRecord]:
        """根据宠物ID获取记录列表"""
        try:
            stmt = (
                select(PetRecordModel)
                .options(
                    selectinload(PetRecordModel.pet),
                    selectinload(PetRecordModel.creator),
                )
                .where(PetRecordModel.pet_id == pet_id)
                .where(PetRecordModel.is_deleted.is_(False))
                .order_by(PetRecordModel.created_at.desc())
            )

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            return self.mapper.to_domain_list(list(models))

        except Exception as e:
            self.logger.error(f"Failed to get pet records by pet_id {pet_id}: {e}")
            raise PetRecordDomainError(f"Failed to get pet records by pet: {e}")

    async def get_by_creator_id(self, creator_id: str) -> list[PetRecord]:
        """根据创建者ID获取记录列表"""
        try:
            stmt = (
                select(PetRecordModel)
                .options(
                    selectinload(PetRecordModel.pet),
                    selectinload(PetRecordModel.creator),
                )
                .where(PetRecordModel.creator_id == creator_id)
                .where(PetRecordModel.is_deleted.is_(False))
                .order_by(PetRecordModel.created_at.desc())
            )

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            return self.mapper.to_domain_list(list(models))

        except Exception as e:
            self.logger.error(
                f"Failed to get pet records by creator_id {creator_id}: {e}"
            )
            raise PetRecordDomainError(f"Failed to get pet records by creator: {e}")

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
        try:
            # 构建搜索条件
            search_conditions = []
            if pet_id:
                search_conditions.append(PetRecordModel.pet_id == pet_id)
            if event_type:
                search_conditions.append(PetRecordModel.event_type == event_type)
            if creator_id:
                search_conditions.append(PetRecordModel.creator_id == creator_id)
            if not include_deleted:
                search_conditions.append(PetRecordModel.is_deleted.is_(False))
            # 注意：由于移除了description字段，搜索功能暂时禁用
            # 如果需要搜索功能，可以考虑在event_data中搜索

            # 组合所有条件
            where_clause = and_(*search_conditions)

            stmt = (
                select(PetRecordModel)
                .options(
                    selectinload(PetRecordModel.pet),
                    selectinload(PetRecordModel.creator),
                )
                .where(where_clause)
            )
            count_stmt = select(func.count(PetRecordModel.id)).where(where_clause)

            # 获取总数
            count_result = await self.session.execute(count_stmt)
            total_count = count_result.scalar()

            # 分页查询
            offset = (page - 1) * page_size
            stmt = (
                stmt.offset(offset)
                .limit(page_size)
                .order_by(PetRecordModel.created_at.desc())
            )

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            records = self.mapper.to_domain_list(list(models))

            return records, total_count

        except Exception as e:
            self.logger.error(
                f"Failed to search pet records with term {search_term}: {e}"
            )
            raise PetRecordDomainError(f"Failed to search pet records: {e}")

    def _generate_query_conditions(
        self,
        search: str | None = None,
        pet_id: str | None = None,
        event_type: PetEventTypeEnum | None = None,
        creator_id: str | None = None,
        include_deleted: bool = False,
    ) -> list[UnaryExpression | ColumnElement]:
        """生成查询条件"""
        conditions = []
        # 注意：由于移除了description字段，搜索功能暂时禁用
        # 如果需要搜索功能，可以考虑在event_data中搜索
        if pet_id:
            conditions.append(PetRecordModel.pet_id == pet_id)
        if event_type:
            conditions.append(PetRecordModel.event_type == event_type)
        if creator_id:
            conditions.append(PetRecordModel.creator_id == creator_id)
        if not include_deleted:
            conditions.append(PetRecordModel.is_deleted.is_(False))
        return conditions
