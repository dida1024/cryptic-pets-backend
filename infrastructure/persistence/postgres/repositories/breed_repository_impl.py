from loguru import logger
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import String, cast

from domain.pets.entities import Breed
from domain.pets.exceptions import BreedNotFoundError, BreedRepositoryError
from domain.pets.repository import BreedRepository
from infrastructure.persistence.postgres.mappers.breed_mapper import BreedMapper
from infrastructure.persistence.postgres.models.breed import BreedModel


class PostgreSQLBreedRepositoryImpl(BreedRepository):
    """品种Repository的PostgreSQL实现"""

    def __init__(self, session: AsyncSession, mapper: BreedMapper):
        self.session = session
        self.mapper = mapper
        self.logger = logger

    async def get_by_id(self, entity_id: str) -> Breed | None:
        """根据ID获取品种"""
        try:
            stmt = (
                select(BreedModel)
                .where(BreedModel.id == entity_id)
                .where(BreedModel.is_deleted.is_(False))
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self.mapper.to_domain(model)

        except Exception as e:
            self.logger.error(f"Failed to get breed by id {entity_id}: {e}")
            raise BreedRepositoryError(f"Failed to get breed: {e}", "get_by_id")

    async def create(self, entity: Breed) -> Breed:
        """创建品种"""
        try:
            model = self.mapper.to_model(entity)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)
            return self.mapper.to_domain(model)
        except Exception as e:
            self.logger.error(f"Failed to create breed {entity.id}: {e}")
            raise BreedRepositoryError(f"Failed to create breed: {e}", "create")

    async def update(self, entity: Breed) -> Breed:
        """更新品种"""
        try:
            # 先检查实体是否存在
            existing_model = await self.session.get(BreedModel, entity.id)
            if existing_model is None or existing_model.is_deleted:
                raise BreedNotFoundError(entity.id)

            # 更新字段
            existing_model.name = entity.name.model_dump()
            existing_model.description = (
                entity.description.model_dump() if entity.description else None
            )
            existing_model.updated_at = entity.updated_at

            await self.session.flush()
            await self.session.refresh(existing_model)

            return self.mapper.to_domain(existing_model)

        except BreedNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to update breed {entity.id}: {e}")
            raise BreedRepositoryError(f"Failed to update breed: {e}", "update")

    async def delete(self, entity_id: str) -> bool:
        """删除品种（软删除）"""
        try:
            model = await self.session.get(BreedModel, entity_id)
            if model is None or model.is_deleted:
                return False

            model.is_deleted = True
            await self.session.flush()

            return True

        except Exception as e:
            self.logger.error(f"Failed to delete breed {entity_id}: {e}")
            raise BreedRepositoryError(f"Failed to delete breed: {e}", "delete")

    async def list_all(
        self,
        page: int = 1,
        page_size: int = 10,
        include_deleted: bool = False
    ) -> tuple[list[Breed], int]:
        """获取品种列表"""
        try:
            # 构建基础查询
            stmt = select(BreedModel)
            count_stmt = select(func.count(BreedModel.id))

            if not include_deleted:
                stmt = stmt.where(BreedModel.is_deleted.is_(False))
                count_stmt = count_stmt.where(BreedModel.is_deleted.is_(False))

            # 获取总数
            count_result = await self.session.execute(count_stmt)
            total_count = count_result.scalar()

            # 分页查询
            offset = (page - 1) * page_size
            stmt = stmt.offset(offset).limit(page_size).order_by(BreedModel.created_at.desc())

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            breeds = self.mapper.to_domain_list(list(models))

            return breeds, total_count

        except Exception as e:
            self.logger.error(f"Failed to list breeds: {e}")
            raise BreedRepositoryError(f"Failed to list breeds: {e}", "list_all")

    async def get_by_name(self, name: str, language: str = "en") -> Breed | None:
        """根据名称获取品种（支持国际化）"""
        try:
            # 使用JSON查询搜索国际化名称
            stmt = (
                select(BreedModel)
                .where(cast(BreedModel.name[language], String) == name)
                .where(BreedModel.is_deleted.is_(False))
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self.mapper.to_domain(model)

        except Exception as e:
            self.logger.error(f"Failed to get breed by name {name}: {e}")
            raise BreedRepositoryError(f"Failed to get breed by name: {e}", "get_by_name")

    async def search_breeds(
        self,
        search_term: str,
        language: str = "en",
        page: int = 1,
        page_size: int = 10,
        include_deleted: bool = False,
    ) -> tuple[list[Breed], int]:
        """搜索品种"""
        try:
            # 构建搜索查询
            search_condition = or_(
                cast(BreedModel.name[language], String).ilike(f"%{search_term}%"),
                cast(BreedModel.description[language], String).ilike(f"%{search_term}%")
            )

            stmt = select(BreedModel).where(search_condition)
            count_stmt = select(func.count(BreedModel.id)).where(search_condition)

            if not include_deleted:
                stmt = stmt.where(BreedModel.is_deleted.is_(False))
                count_stmt = count_stmt.where(BreedModel.is_deleted.is_(False))

            # 获取总数
            count_result = await self.session.execute(count_stmt)
            total_count = count_result.scalar()

            # 分页查询
            offset = (page - 1) * page_size
            stmt = stmt.offset(offset).limit(page_size).order_by(BreedModel.created_at.desc())

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            breeds = self.mapper.to_domain_list(list(models))

            return breeds, total_count

        except Exception as e:
            self.logger.error(f"Failed to search breeds with term {search_term}: {e}")
            raise BreedRepositoryError(f"Failed to search breeds: {e}", "search_breeds")
