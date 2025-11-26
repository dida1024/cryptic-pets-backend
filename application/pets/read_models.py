"""读模型定义，服务于宠物查询端的优化读"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.pets.value_objects import GenderEnum


@dataclass(slots=True)
class PetSearchRow:
    """表示一次宠物搜索结果中的一行数据"""

    id: str
    name: str
    gender: GenderEnum
    created_at: datetime
    owner_id: str | None
    owner_name: str | None
    breed_id: str | None
    breed_name: dict[str, str] | None


class PetSearchReadRepository:
    """宠物搜索读模型仓储接口"""

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
        raise NotImplementedError

