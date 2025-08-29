from loguru import logger
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import String, cast

from domain.pets.entities import Morphology
from domain.pets.exceptions import MorphologyNotFoundError, MorphologyRepositoryError
from domain.pets.repository import MorphologyRepository
from infrastructure.persistence.postgres.mappers import MorphologyMapper
from infrastructure.persistence.postgres.models.morph_gene_mapping import (
    MorphGeneMappingModel,
)
from infrastructure.persistence.postgres.models.morphology import MorphologyModel


class PostgreSQLMorphologyRepositoryImpl(MorphologyRepository):
    """形态学Repository的PostgreSQL实现"""

    def __init__(self, session: AsyncSession, mapper: MorphologyMapper):
        self.session = session
        self.mapper = mapper
        self.logger = logger

    async def get_by_id(self, entity_id: str) -> Morphology | None:
        """根据ID获取形态学"""
        try:
            stmt = (
                select(MorphologyModel)
                .options(
                    selectinload(MorphologyModel.gene_mappings).selectinload(
                        MorphGeneMappingModel.gene
                    )
                )
                .where(MorphologyModel.id == entity_id)
                .where(not MorphologyModel.is_deleted)
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self.mapper.to_domain(model)

        except Exception as e:
            self.logger.error(f"Failed to get morphology by id {entity_id}: {e}")
            raise MorphologyRepositoryError(
                f"Failed to get morphology: {e}", "get_by_id"
            )

    async def create(self, entity: Morphology) -> Morphology:
        """创建形态学"""
        try:
            model = self.mapper.to_model(entity)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)

            return self.mapper.to_domain(model)

        except Exception as e:
            self.logger.error(f"Failed to create morphology {entity.id}: {e}")
            raise MorphologyRepositoryError(
                f"Failed to create morphology: {e}", "create"
            )

    async def update(self, entity: Morphology) -> Morphology:
        """更新形态学"""
        try:
            existing_model = await self.session.get(MorphologyModel, entity.id)
            if existing_model is None or existing_model.is_deleted:
                raise MorphologyNotFoundError(entity.id)

            # 更新字段
            existing_model.name = entity.name
            existing_model.description = entity.description
            existing_model.updated_at = entity.updated_at

            await self.session.flush()
            await self.session.refresh(existing_model)

            return self.mapper.to_domain(existing_model)

        except MorphologyNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to update morphology {entity.id}: {e}")
            raise MorphologyRepositoryError(
                f"Failed to update morphology: {e}", "update"
            )

    async def delete(self, entity_id: str) -> bool:
        """删除形态学（软删除）"""
        try:
            model = await self.session.get(MorphologyModel, entity_id)
            if model is None or model.is_deleted:
                return False

            model.is_deleted = True
            await self.session.flush()

            return True

        except Exception as e:
            self.logger.error(f"Failed to delete morphology {entity_id}: {e}")
            raise MorphologyRepositoryError(
                f"Failed to delete morphology: {e}", "delete"
            )

    async def list_all(
        self, page: int = 1, page_size: int = 10, include_deleted: bool = False
    ) -> tuple[list[Morphology], int]:
        """获取形态学列表"""
        try:
            stmt = select(MorphologyModel).options(
                selectinload(MorphologyModel.gene_mappings).selectinload(
                    MorphGeneMappingModel.gene
                )
            )
            count_stmt = select(func.count(MorphologyModel.id))

            if not include_deleted:
                stmt = stmt.where(not MorphologyModel.is_deleted)
                count_stmt = count_stmt.where(not MorphologyModel.is_deleted)

            # 获取总数
            count_result = await self.session.execute(count_stmt)
            total_count = count_result.scalar()

            # 分页查询
            offset = (page - 1) * page_size
            stmt = (
                stmt.offset(offset)
                .limit(page_size)
                .order_by(MorphologyModel.created_at.desc())
            )

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            morphologies = self.mapper.to_domain_list(list(models))

            return morphologies, total_count

        except Exception as e:
            self.logger.error(f"Failed to list morphologies: {e}")
            raise MorphologyRepositoryError(
                f"Failed to list morphologies: {e}", "list_all"
            )

    async def get_by_gene_combination(self, gene_ids: list[str]) -> list[Morphology]:
        """根据基因组合获取形态学列表"""
        try:
            # 查找包含所有指定基因的形态学
            stmt = (
                select(MorphologyModel)
                .options(
                    selectinload(MorphologyModel.gene_mappings).selectinload(
                        MorphGeneMappingModel.gene
                    )
                )
                .join(
                    MorphGeneMappingModel,
                    MorphologyModel.id == MorphGeneMappingModel.morphology_id,
                )
                .where(MorphGeneMappingModel.gene_id.in_(gene_ids))
                .where(not MorphologyModel.is_deleted)
                .group_by(MorphologyModel.id)
                .having(func.count(MorphGeneMappingModel.gene_id) == len(gene_ids))
            )

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            return self.mapper.to_domain_list(list(models))

        except Exception as e:
            self.logger.error(
                f"Failed to get morphologies by gene combination {gene_ids}: {e}"
            )
            raise MorphologyRepositoryError(
                f"Failed to get morphologies by gene combination: {e}",
                "get_by_gene_combination",
            )

    async def get_by_required_genes(self, gene_ids: list[str]) -> list[Morphology]:
        """根据必需基因获取形态学列表"""
        try:
            stmt = (
                select(MorphologyModel)
                .options(
                    selectinload(MorphologyModel.gene_mappings).selectinload(
                        MorphGeneMappingModel.gene
                    )
                )
                .join(
                    MorphGeneMappingModel,
                    MorphologyModel.id == MorphGeneMappingModel.morphology_id,
                )
                .where(MorphGeneMappingModel.gene_id.in_(gene_ids))
                .where(MorphGeneMappingModel.is_required)
                .where(not MorphologyModel.is_deleted)
                .group_by(MorphologyModel.id)
                .having(func.count(MorphGeneMappingModel.gene_id) == len(gene_ids))
            )

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            return self.mapper.to_domain_list(list(models))

        except Exception as e:
            self.logger.error(
                f"Failed to get morphologies by required genes {gene_ids}: {e}"
            )
            raise MorphologyRepositoryError(
                f"Failed to get morphologies by required genes: {e}",
                "get_by_required_genes",
            )

    async def get_morphologies_containing_gene(self, gene_id: str) -> list[Morphology]:
        """获取包含指定基因的所有形态学"""
        try:
            stmt = (
                select(MorphologyModel)
                .options(
                    selectinload(MorphologyModel.gene_mappings).selectinload(
                        MorphGeneMappingModel.gene
                    )
                )
                .join(
                    MorphGeneMappingModel,
                    MorphologyModel.id == MorphGeneMappingModel.morphology_id,
                )
                .where(MorphGeneMappingModel.gene_id == gene_id)
                .where(not MorphologyModel.is_deleted)
            )

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            return self.mapper.to_domain_list(list(models))

        except Exception as e:
            self.logger.error(
                f"Failed to get morphologies containing gene {gene_id}: {e}"
            )
            raise MorphologyRepositoryError(
                f"Failed to get morphologies containing gene: {e}",
                "get_morphologies_containing_gene",
            )

    async def search_morphologies(
        self,
        search_term: str,
        gene_ids: list[str] | None = None,
        language: str = "en",
        page: int = 1,
        page_size: int = 10,
        include_deleted: bool = False,
    ) -> tuple[list[Morphology], int]:
        """搜索形态学"""
        try:
            # 构建基础查询
            stmt = select(MorphologyModel).options(
                selectinload(MorphologyModel.gene_mappings).selectinload(
                    MorphGeneMappingModel.gene
                )
            )
            count_stmt = select(func.count(MorphologyModel.id))

            # 搜索条件
            search_conditions = [
                or_(
                    cast(MorphologyModel.name[language], String).ilike(f"%{search_term}%"),
                    cast(MorphologyModel.description[language], String).ilike(
                        f"%{search_term}%"
                    ),
                )
            ]

            # 基因过滤条件
            if gene_ids:
                stmt = stmt.join(
                    MorphGeneMappingModel,
                    MorphologyModel.id == MorphGeneMappingModel.morphology_id,
                )
                count_stmt = count_stmt.join(
                    MorphGeneMappingModel,
                    MorphologyModel.id == MorphGeneMappingModel.morphology_id,
                )
                search_conditions.append(MorphGeneMappingModel.gene_id.in_(gene_ids))

            if not include_deleted:
                search_conditions.append(not MorphologyModel.is_deleted)

            # 组合所有条件
            where_clause = and_(*search_conditions)

            stmt = stmt.where(where_clause)
            count_stmt = count_stmt.where(where_clause)

            # 如果有基因过滤，需要去重
            if gene_ids:
                stmt = stmt.group_by(MorphologyModel.id)
                count_stmt = (
                    select(func.count(func.distinct(MorphologyModel.id)))
                    .select_from(
                        MorphologyModel.join(
                            MorphGeneMappingModel,
                            MorphologyModel.id == MorphGeneMappingModel.morphology_id,
                        )
                    )
                    .where(where_clause)
                )

            # 获取总数
            count_result = await self.session.execute(count_stmt)
            total_count = count_result.scalar()

            # 分页查询
            offset = (page - 1) * page_size
            stmt = (
                stmt.offset(offset)
                .limit(page_size)
                .order_by(MorphologyModel.created_at.desc())
            )

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            morphologies = self.mapper.to_domain_list(list(models))

            return morphologies, total_count

        except Exception as e:
            self.logger.error(
                f"Failed to search morphologies with term {search_term}: {e}"
            )
            raise MorphologyRepositoryError(
                f"Failed to search morphologies: {e}", "search_morphologies"
            )
