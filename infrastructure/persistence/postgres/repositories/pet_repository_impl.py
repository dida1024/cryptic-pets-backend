
from loguru import logger
from sqlalchemy import ColumnElement, UnaryExpression, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import String, cast

from domain.common.event_publisher import EventPublisher
from domain.pets.entities import Pet
from domain.pets.exceptions import PetNotFoundError, PetRepositoryError
from domain.pets.repository import PetRepository
from infrastructure.persistence.postgres.mappers import PetMapper
from infrastructure.persistence.postgres.models.morph_gene_mapping import (
    MorphGeneMappingModel,
)
from infrastructure.persistence.postgres.models.morphology import MorphologyModel
from infrastructure.persistence.postgres.models.pet import PetModel
from infrastructure.persistence.postgres.repositories.event_aware_repository import (
    EventAwareRepository,
)


class PostgreSQLPetRepositoryImpl(EventAwareRepository[Pet], PetRepository):
    """宠物Repository的PostgreSQL实现"""

    def __init__(self, session: AsyncSession, mapper: PetMapper, event_publisher: EventPublisher):
        super().__init__(event_publisher)
        self.session = session
        self.mapper = mapper
        self.logger = logger

    async def get_by_id(self, entity_id: str) -> Pet | None:
        """根据ID获取宠物"""
        try:
            stmt = (
                select(PetModel)
                .options(
                    selectinload(PetModel.breed),
                    selectinload(PetModel.morphology).selectinload(MorphologyModel.gene_mappings),
                    selectinload(PetModel.extra_gene_list).selectinload(MorphGeneMappingModel.gene)
                )
                .where(PetModel.id == entity_id)
                .where(PetModel.is_deleted.is_(False))
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self.mapper.to_domain(model)

        except Exception as e:
            self.logger.error(f"Failed to get pet by id {entity_id}: {e}")
            raise PetRepositoryError(f"Failed to get pet: {e}", "get_by_id")

    async def create(self, entity: Pet) -> Pet:
        """创建宠物"""
        try:
            model = self.mapper.to_model(entity)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model, attribute_names=['breed', 'morphology', 'extra_gene_list', 'owner'])

            # 转换为领域实体并发布事件
            created_pet = self.mapper.to_domain(model)
            await self._publish_events_from_entity(created_pet)

            return created_pet

        except Exception as e:
            self.logger.error(f"Failed to create pet {entity.id}: {e}")
            raise PetRepositoryError(f"Failed to create pet: {e}", "create")

    async def update(self, entity: Pet) -> Pet:
        """更新宠物"""
        try:
            existing_model = await self.session.get(PetModel, entity.id)
            if existing_model is None or existing_model.is_deleted:
                raise PetNotFoundError(entity.id)

            # 更新字段
            existing_model.name = entity.name
            existing_model.description = entity.description
            existing_model.birth_date = entity.birth_date
            existing_model.owner_id = entity.owner_id
            existing_model.breed_id = entity.breed_id
            existing_model.gender = entity.gender
            existing_model.morphology_id = entity.morphology_id
            existing_model.updated_at = entity.updated_at

            await self.session.flush()
            await self.session.refresh(existing_model)

            # 转换为领域实体并发布事件
            updated_pet = self.mapper.to_domain(existing_model)
            await self._publish_events_from_entity(updated_pet)

            return updated_pet

        except PetNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to update pet {entity.id}: {e}")
            raise PetRepositoryError(f"Failed to update pet: {e}", "update")

    async def delete(self, entity_id: str) -> bool:
        """删除宠物（软删除）"""
        try:
            model = await self.session.get(PetModel, entity_id)
            if model is None or model.is_deleted:
                return False

            # 先获取实体以发布删除事件
            pet_entity = self.mapper.to_domain(model)

            model.is_deleted = True
            await self.session.flush()

            # 发布删除事件
            await self._publish_events_from_entity(pet_entity)

            return True

        except Exception as e:
            self.logger.error(f"Failed to delete pet {entity_id}: {e}")
            raise PetRepositoryError(f"Failed to delete pet: {e}", "delete")

    async def list_all(
        self,
        page: int = 1,
        page_size: int = 10,
        search: str = None,
        owner_id: str = None,
        include_deleted: bool = False
    ) -> tuple[list[Pet], int]:
        """获取宠物列表"""
        try:
            stmt = (
                select(
                    PetModel,
                    func.count(PetModel.id).over().label("total_count")
                )
                .options(
                    selectinload(PetModel.breed),
                    selectinload(PetModel.morphology),
                    selectinload(PetModel.extra_gene_list),
                    selectinload(PetModel.owner)
                )
            )
            conditions = self._generate_query_conditions(search, owner_id, include_deleted)
            if conditions:
                stmt = stmt.where(*conditions)

            stmt = stmt.offset((page - 1) * page_size).limit(page_size).order_by(PetModel.created_at.desc())

            result = await self.session.execute(stmt)
            rows = result.all()

            if not rows:
                return [], 0
            total_count = rows[0].total_count
            models = [row.PetModel for row in rows]
            pets = self.mapper.to_domain_list(models)
            return pets, total_count

        except Exception as e:
            self.logger.error(f"Failed to list pets: {e}")
            raise PetRepositoryError(f"Failed to list pets: {e}", "list_all")

    def _generate_query_conditions(
        self,
        search: str = None,
        owner_id: str = None,
        include_deleted: bool = False
    ) -> list[UnaryExpression | ColumnElement]:
        """生成查询条件"""
        conditions = []
        if search:
            conditions.append(PetModel.name.ilike(f"%{search}%"))
        if owner_id:
            conditions.append(PetModel.owner_id == owner_id)
        if not include_deleted:
            conditions.append(PetModel.is_deleted.is_(False))
        return conditions

    async def get_by_owner_id(self, owner_id: str) -> list[Pet]:
        """根据主人ID获取宠物列表"""
        try:
            stmt = (
                select(PetModel)
                .options(
                    selectinload(PetModel.breed),
                    selectinload(PetModel.morphology),
                    selectinload(PetModel.extra_gene_list)
                )
                .where(PetModel.owner_id == owner_id)
                .where(PetModel.is_deleted.is_(False))
                .order_by(PetModel.created_at.desc())
            )

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            return self.mapper.to_domain_list(list(models))

        except Exception as e:
            self.logger.error(f"Failed to get pets by owner_id {owner_id}: {e}")
            raise PetRepositoryError(f"Failed to get pets by owner: {e}", "get_by_owner_id")

    async def get_by_breed_id(self, breed_id: str) -> list[Pet]:
        """根据品种ID获取宠物列表"""
        try:
            stmt = (
                select(PetModel)
                .options(
                    selectinload(PetModel.breed),
                    selectinload(PetModel.morphology),
                    selectinload(PetModel.extra_gene_list)
                )
                .where(PetModel.breed_id == breed_id)
                .where(PetModel.is_deleted.is_(False))
                .order_by(PetModel.created_at.desc())
            )

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            return self.mapper.to_domain_list(list(models))

        except Exception as e:
            self.logger.error(f"Failed to get pets by breed_id {breed_id}: {e}")
            raise PetRepositoryError(f"Failed to get pets by breed: {e}", "get_by_breed_id")

    async def get_by_morphology_id(self, morphology_id: str) -> list[Pet]:
        """根据形态学ID获取宠物列表"""
        try:
            stmt = (
                select(PetModel)
                .options(
                    selectinload(PetModel.breed),
                    selectinload(PetModel.morphology),
                    selectinload(PetModel.extra_gene_list)
                )
                .where(PetModel.morphology_id == morphology_id)
                .where(PetModel.is_deleted.is_(False))
                .order_by(PetModel.created_at.desc())
            )

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            return self.mapper.to_domain_list(list(models))

        except Exception as e:
            self.logger.error(f"Failed to get pets by morphology_id {morphology_id}: {e}")
            raise PetRepositoryError(f"Failed to get pets by morphology: {e}", "get_by_morphology_id")

    async def get_by_name(self, name: str, language: str = "en") -> Pet | None:
        """根据名称获取宠物（支持国际化）"""
        try:
            stmt = (
                select(PetModel)
                .options(
                    selectinload(PetModel.breed),
                    selectinload(PetModel.morphology),
                    selectinload(PetModel.extra_gene_list)
                )
                .where(cast(PetModel.name[language], String) == name)
                .where(PetModel.is_deleted.is_(False))
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self.mapper.to_domain(model)

        except Exception as e:
            self.logger.error(f"Failed to get pet by name {name}: {e}")
            raise PetRepositoryError(f"Failed to get pet by name: {e}", "get_by_name")

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
        """搜索宠物"""
        try:
            # 构建搜索条件
            search_conditions = [
                or_(
                    cast(PetModel.name["en"], String).ilike(f"%{search_term}%"),
                    cast(PetModel.name["zh"], String).ilike(f"%{search_term}%")
                )
            ]

            # 添加过滤条件
            if owner_id:
                search_conditions.append(PetModel.owner_id == owner_id)

            if breed_id:
                search_conditions.append(PetModel.breed_id == breed_id)

            if morphology_id:
                search_conditions.append(PetModel.morphology_id == morphology_id)

            if not include_deleted:
                search_conditions.append(PetModel.is_deleted.is_(False))

            # 组合所有条件
            where_clause = and_(*search_conditions)

            stmt = (
                select(PetModel)
                .options(
                    selectinload(PetModel.breed),
                    selectinload(PetModel.morphology),
                    selectinload(PetModel.extra_gene_list)
                )
                .where(where_clause)
            )
            count_stmt = select(func.count(PetModel.id)).where(where_clause)

            # 获取总数
            count_result = await self.session.execute(count_stmt)
            total_count = count_result.scalar()

            # 分页查询
            offset = (page - 1) * page_size
            stmt = stmt.offset(offset).limit(page_size).order_by(PetModel.created_at.desc())

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            pets = self.mapper.to_domain_list(list(models))

            return pets, total_count

        except Exception as e:
            self.logger.error(f"Failed to search pets with term {search_term}: {e}")
            raise PetRepositoryError(f"Failed to search pets: {e}", "search_pets")

    async def exists_by_name(self, name: str, exclude_id: str | None = None) -> bool:
        """检查指定名称的宠物是否存在（可选排除ID）"""
        try:
            stmt = select(func.count(PetModel.id)).where(
                PetModel.name == name,
                PetModel.is_deleted.is_(False),
            )
            if exclude_id:
                stmt = stmt.where(PetModel.id != exclude_id)
            result = await self.session.execute(stmt)
            count = result.scalar() or 0
            return count > 0
        except Exception as e:
            self.logger.error(f"Failed to check pet exists by name {name}: {e}")
            raise PetRepositoryError(f"Failed to check exists_by_name: {e}", "exists_by_name")
