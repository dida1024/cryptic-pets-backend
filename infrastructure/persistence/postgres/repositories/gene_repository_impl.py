from loguru import logger
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.pets.entities import Gene
from domain.pets.exceptions import GeneNotFoundError, GeneRepositoryError
from domain.pets.repository import GeneRepository
from domain.pets.value_objects import GeneCategoryEnum, InheritanceTypeEnum
from infrastructure.persistence.postgres.mappers.gene_mapper import GeneMapper
from infrastructure.persistence.postgres.models.gene import Gene as GeneModel


class PostgreSQLGeneRepositoryImpl(GeneRepository):
    """基因Repository的PostgreSQL实现"""

    def __init__(self, session: AsyncSession, mapper: GeneMapper):
        self.session = session
        self.mapper = mapper
        self.logger = logger

    async def get_by_id(self, entity_id: str) -> Gene | None:
        """根据ID获取基因"""
        try:
            stmt = (
                select(GeneModel)
                .where(GeneModel.id == entity_id)
                .where(not GeneModel.is_deleted)
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self.mapper.to_domain(model)

        except Exception as e:
            self.logger.error(f"Failed to get gene by id {entity_id}: {e}")
            raise GeneRepositoryError(f"Failed to get gene: {e}", "get_by_id")

    async def create(self, entity: Gene) -> Gene:
        """创建基因"""
        try:
            model = self.mapper.to_model(entity)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)

            return self.mapper.to_domain(model)

        except Exception as e:
            self.logger.error(f"Failed to create gene {entity.id}: {e}")
            raise GeneRepositoryError(f"Failed to create gene: {e}", "create")

    async def update(self, entity: Gene) -> Gene:
        """更新基因"""
        try:
            existing_model = await self.session.get(GeneModel, entity.id)
            if existing_model is None or existing_model.is_deleted:
                raise GeneNotFoundError(entity.id)

            # 更新字段
            existing_model.name = entity.name
            existing_model.alias = entity.alias
            existing_model.description = entity.description
            existing_model.notation = entity.notation
            existing_model.inheritance_type = entity.inheritance_type
            existing_model.category = entity.category
            existing_model.updated_at = entity.updated_at
            existing_model.version = entity.version

            await self.session.flush()
            await self.session.refresh(existing_model)

            return self.mapper.to_domain(existing_model)

        except GeneNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to update gene {entity.id}: {e}")
            raise GeneRepositoryError(f"Failed to update gene: {e}", "update")

    async def delete(self, entity_id: str) -> bool:
        """删除基因（软删除）"""
        try:
            model = await self.session.get(GeneModel, entity_id)
            if model is None or model.is_deleted:
                return False

            model.is_deleted = True
            await self.session.flush()

            return True

        except Exception as e:
            self.logger.error(f"Failed to delete gene {entity_id}: {e}")
            raise GeneRepositoryError(f"Failed to delete gene: {e}", "delete")

    async def list_all(
        self,
        page: int = 1,
        page_size: int = 10,
        include_deleted: bool = False
    ) -> tuple[list[Gene], int]:
        """获取基因列表"""
        try:
            stmt = select(GeneModel)
            count_stmt = select(func.count(GeneModel.id))

            if not include_deleted:
                stmt = stmt.where(not GeneModel.is_deleted)
                count_stmt = count_stmt.where(not GeneModel.is_deleted)

            # 获取总数
            count_result = await self.session.execute(count_stmt)
            total_count = count_result.scalar()

            # 分页查询
            offset = (page - 1) * page_size
            stmt = stmt.offset(offset).limit(page_size).order_by(GeneModel.created_at.desc())

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            genes = self.mapper.to_domain_list(list(models))

            return genes, total_count

        except Exception as e:
            self.logger.error(f"Failed to list genes: {e}")
            raise GeneRepositoryError(f"Failed to list genes: {e}", "list_all")

    async def get_by_category(self, category: GeneCategoryEnum) -> list[Gene]:
        """根据基因类别获取基因列表"""
        try:
            stmt = (
                select(GeneModel)
                .where(GeneModel.category == category)
                .where(not GeneModel.is_deleted)
                .order_by(GeneModel.name)
            )
            result = await self.session.execute(stmt)
            models = result.scalars().all()

            return self.mapper.to_domain_list(list(models))

        except Exception as e:
            self.logger.error(f"Failed to get genes by category {category}: {e}")
            raise GeneRepositoryError(f"Failed to get genes by category: {e}", "get_by_category")

    async def get_by_inheritance_type(self, inheritance_type: InheritanceTypeEnum) -> list[Gene]:
        """根据遗传类型获取基因列表"""
        try:
            stmt = (
                select(GeneModel)
                .where(GeneModel.inheritance_type == inheritance_type)
                .where(not GeneModel.is_deleted)
                .order_by(GeneModel.name)
            )
            result = await self.session.execute(stmt)
            models = result.scalars().all()

            return self.mapper.to_domain_list(list(models))

        except Exception as e:
            self.logger.error(f"Failed to get genes by inheritance type {inheritance_type}: {e}")
            raise GeneRepositoryError(f"Failed to get genes by inheritance type: {e}", "get_by_inheritance_type")

    async def get_by_notation(self, notation: str) -> Gene | None:
        """根据基因标记获取基因"""
        try:
            stmt = (
                select(GeneModel)
                .where(GeneModel.notation == notation)
                .where(not GeneModel.is_deleted)
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self.mapper.to_domain(model)

        except Exception as e:
            self.logger.error(f"Failed to get gene by notation {notation}: {e}")
            raise GeneRepositoryError(f"Failed to get gene by notation: {e}", "get_by_notation")

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
        """搜索基因"""
        try:
            # 构建搜索条件
            search_conditions = [
                or_(
                    GeneModel.name[language].astext.ilike(f"%{search_term}%"),
                    GeneModel.alias[language].astext.ilike(f"%{search_term}%"),
                    GeneModel.description[language].astext.ilike(f"%{search_term}%"),
                    GeneModel.notation.ilike(f"%{search_term}%")
                )
            ]

            # 添加过滤条件
            if category is not None:
                search_conditions.append(GeneModel.category == category)

            if inheritance_type is not None:
                search_conditions.append(GeneModel.inheritance_type == inheritance_type)

            if not include_deleted:
                search_conditions.append(not GeneModel.is_deleted)

            # 组合所有条件
            where_clause = and_(*search_conditions)

            stmt = select(GeneModel).where(where_clause)
            count_stmt = select(func.count(GeneModel.id)).where(where_clause)

            # 获取总数
            count_result = await self.session.execute(count_stmt)
            total_count = count_result.scalar()

            # 分页查询
            offset = (page - 1) * page_size
            stmt = stmt.offset(offset).limit(page_size).order_by(GeneModel.created_at.desc())

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            genes = self.mapper.to_domain_list(list(models))

            return genes, total_count

        except Exception as e:
            self.logger.error(f"Failed to search genes with term {search_term}: {e}")
            raise GeneRepositoryError(f"Failed to search genes: {e}", "search_genes")
