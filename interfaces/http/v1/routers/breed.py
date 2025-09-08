from fastapi import APIRouter, Depends, Path, Query, status

from application.breeds.commands import (
    CreateBreedCommand,
    DeleteBreedCommand,
    ListBreedsQuery,
    SearchBreedsQuery,
    UpdateBreedCommand,
)
from application.breeds.handlers import BreedService
from infrastructure.dependencies import get_breed_service
from interfaces.http.base_response import ApiResponse, PaginatedResponse
from interfaces.http.decorators import handle_exceptions
from interfaces.http.v1.schemas.breed_schemas import (
    BreedResponse,
    CreateBreedRequest,
    UpdateBreedRequest,
)

router = APIRouter(prefix="/breeds", tags=["breeds"])


@router.post(
    "",
    response_model=ApiResponse[BreedResponse],
    status_code=status.HTTP_201_CREATED,
    summary="创建品种",
)
@handle_exceptions
async def create_breed(
    request: CreateBreedRequest,
    breed_service: BreedService = Depends(get_breed_service),
) -> ApiResponse[BreedResponse]:
    command = CreateBreedCommand(name=request.name, description=request.description)
    breed = await breed_service.create_breed(command)
    return ApiResponse.success(data=BreedResponse.model_validate(breed.model_dump()), message="Breed created successfully")


@router.get(
    "/{breed_id}",
    response_model=ApiResponse[BreedResponse],
    summary="获取品种详情",
)
@handle_exceptions
async def get_breed(
    breed_id: str = Path(..., description="品种ID"),
    breed_service: BreedService = Depends(get_breed_service),
) -> ApiResponse[BreedResponse]:
    breed = await breed_service.get_breed_by_id(breed_id)
    return ApiResponse.success(data=BreedResponse.model_validate(breed.model_dump()))


@router.put(
    "/{breed_id}",
    response_model=ApiResponse[BreedResponse],
    summary="更新品种",
)
@handle_exceptions
async def update_breed(
    breed_id: str,
    request: UpdateBreedRequest,
    breed_service: BreedService = Depends(get_breed_service),
) -> ApiResponse[BreedResponse]:
    command = UpdateBreedCommand(breed_id=breed_id, name=request.name, description=request.description)
    breed = await breed_service.update_breed(command)
    return ApiResponse.success(data=BreedResponse.model_validate(breed.model_dump()), message="Breed updated successfully")


@router.delete(
    "/{breed_id}",
    response_model=ApiResponse[dict],
    summary="删除品种",
)
@handle_exceptions
async def delete_breed(
    breed_id: str,
    breed_service: BreedService = Depends(get_breed_service),
) -> ApiResponse[dict]:
    success = await breed_service.delete_breed(DeleteBreedCommand(breed_id=breed_id))
    return ApiResponse.success(data={"deleted": success})


@router.get(
    "",
    response_model=PaginatedResponse[BreedResponse],
    summary="获取品种列表",
)
@handle_exceptions
async def list_breeds(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    include_deleted: bool = Query(False, description="是否包含已删除"),
    breed_service: BreedService = Depends(get_breed_service),
) -> PaginatedResponse[BreedResponse]:
    breeds, total = await breed_service.list_all(ListBreedsQuery(page=page, page_size=page_size, include_deleted=include_deleted))
    items = [BreedResponse.model_validate(b.model_dump()) for b in breeds]
    return PaginatedResponse.create(items=items, total=total, page=page, page_size=page_size)


@router.get(
    "/search",
    response_model=PaginatedResponse[BreedResponse],
    summary="搜索品种",
)
@handle_exceptions
async def search_breeds(
    q: str = Query(..., description="关键字"),
    language: str = Query("en", description="语言"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    include_deleted: bool = Query(False),
    breed_service: BreedService = Depends(get_breed_service),
) -> PaginatedResponse[BreedResponse]:
    breeds, total = await breed_service.search(
        SearchBreedsQuery(search=q, language=language, page=page, page_size=page_size, include_deleted=include_deleted)
    )
    items = [BreedResponse.model_validate(b.model_dump()) for b in breeds]
    return PaginatedResponse.create(items=items, total=total, page=page, page_size=page_size)


