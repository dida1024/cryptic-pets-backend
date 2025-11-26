"""宠物搜索读模型的PostgreSQL实现"""

from __future__ import annotations

from collections.abc import Sequence

from loguru import logger
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.pets.read_models import PetSearchReadRepository, PetSearchRow
from domain.pets.value_objects import GenderEnum
from infrastructure.persistence.postgres.models.breed import BreedModel
from infrastructure.persistence.postgres.models.pet import PetModel
from infrastructure.persistence.postgres.models.user import UserModel


class PostgreSQLPetSearchReadRepository(PetSearchReadRepository):
    """使用单次SQL查询返回宠物及其关键信息的读仓储"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def search_pets(
        self,
        search_term: str | None = None,
        owner_id: str | None = None,
        breed_id: str | None = None,
        morphology_id: str | None = None,
        page: int = 1,
        page_size: int = 10,
        include_deleted: bool = False,
    ) -> tuple[list[PetSearchRow], int]:
        try:
            conditions = []
            if owner_id:
                conditions.append(PetModel.owner_id == owner_id)
            if breed_id:
                conditions.append(PetModel.breed_id == breed_id)
            if morphology_id:
                conditions.append(PetModel.morphology_id == morphology_id)
            if not include_deleted:
                conditions.append(PetModel.is_deleted.is_(False))
            if search_term:
                conditions.append(PetModel.name.ilike(f"%{search_term}%"))

            where_clause = and_(*conditions) if conditions else None

            stmt = (
                select(
                    PetModel.id,
                    PetModel.name,
                    PetModel.gender,
                    PetModel.created_at,
                    PetModel.owner_id,
                    UserModel.username,
                    UserModel.full_name,
                    PetModel.breed_id,
                    BreedModel.name.label("breed_name"),
                )
                .select_from(PetModel)
                .join(UserModel, and_(UserModel.id == PetModel.owner_id, UserModel.is_deleted.is_(False)), isouter=True)
                .join(BreedModel, and_(BreedModel.id == PetModel.breed_id, BreedModel.is_deleted.is_(False)), isouter=True)
            )

            count_stmt = select(func.count(PetModel.id)).select_from(PetModel)
            if where_clause is not None:
                stmt = stmt.where(where_clause)
                count_stmt = count_stmt.where(where_clause)

            count_result = await self.session.execute(count_stmt)
            total_count = count_result.scalar() or 0

            offset = (page - 1) * page_size
            stmt = stmt.order_by(PetModel.created_at.desc()).offset(offset).limit(page_size)

            result = await self.session.execute(stmt)
            rows: Sequence = result.all()

            return [self._to_row(row) for row in rows], total_count

        except Exception as exc:
            logger.error(f"Failed to search pets read model: {exc}")
            raise

    @staticmethod
    def _to_row(row: Sequence) -> PetSearchRow:
        owner_username = getattr(row, "username", None)
        owner_full_name = getattr(row, "full_name", None)
        owner_name = owner_username or owner_full_name

        breed_name = getattr(row, "breed_name", None)

        return PetSearchRow(
            id=row.id,
            name=row.name,
            gender=GenderEnum(row.gender) if not isinstance(row.gender, GenderEnum) else row.gender,
            created_at=row.created_at,
            owner_id=row.owner_id,
            owner_name=owner_name,
            breed_id=row.breed_id,
            breed_name=breed_name,
        )

