
from loguru import logger
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domain.pets.entities import Pet
from domain.pets.exceptions import PetNotFoundError, PetRepositoryError
from domain.pets.repository import PetRepository
from infrastructure.persistence.postgres.mappers import PetMapper
from infrastructure.persistence.postgres.models.morph_gene_mapping import (
    MorphGeneMapping as MorphGeneMappingModel,
)
from infrastructure.persistence.postgres.models.morphology import (
    Morphology as MorphologyModel,
)
from infrastructure.persistence.postgres.models.pet import PetModel


class PostgreSQLPetRepositoryImpl(PetRepository):
    """宠物Repository的PostgreSQL实现"""

    def __init__(self, session: AsyncSession, mapper: PetMapper):
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
                .where(not PetModel.is_deleted)
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
            await self.session.refresh(model)

            return self.mapper.to_domain(model)

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
            existing_model.birth_date = entity.birth_date
            existing_model.owner_id = entity.owner.id
            existing_model.breed_id = entity.breed.id if entity.breed else None
            existing_model.gender = entity.gender
            existing_model.morphology_id = entity.morphology.id if entity.morphology else None
            existing_model.updated_at = entity.updated_at
            existing_model.version = entity.version

            await self.session.flush()
            await self.session.refresh(existing_model)

            return self.mapper.to_domain(existing_model)

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

            model.is_deleted = True
            await self.session.flush()

            return True

        except Exception as e:
            self.logger.error(f"Failed to delete pet {entity_id}: {e}")
            raise PetRepositoryError(f"Failed to delete pet: {e}", "delete")

    async def list_all(
        self,
        page: int = 1,
        page_size: int = 10,
        include_deleted: bool = False
    ) -> tuple[list[Pet], int]:
        """获取宠物列表"""
        try:
            stmt = (
                select(PetModel)
                .options(
                    selectinload(PetModel.breed),
                    selectinload(PetModel.morphology),
                    selectinload(PetModel.extra_gene_list)
                )
            )
            count_stmt = select(func.count(PetModel.id))

            if not include_deleted:
                stmt = stmt.where(not PetModel.is_deleted)
                count_stmt = count_stmt.where(not PetModel.is_deleted)

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
            self.logger.error(f"Failed to list pets: {e}")
            raise PetRepositoryError(f"Failed to list pets: {e}", "list_all")

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
                .where(not PetModel.is_deleted)
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
                .where(not PetModel.is_deleted)
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
                .where(not PetModel.is_deleted)
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
                .where(PetModel.name[language].astext == name)
                .where(not PetModel.is_deleted)
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
                    PetModel.name["en"].astext.ilike(f"%{search_term}%"),
                    PetModel.name["zh"].astext.ilike(f"%{search_term}%")
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
                search_conditions.append(not PetModel.is_deleted)

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
