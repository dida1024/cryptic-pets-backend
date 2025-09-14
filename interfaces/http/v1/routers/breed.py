from fastapi import APIRouter, Depends, Path, Query, status

from application.breeds.command_handlers import (
    CreateBreedHandler,
    DeleteBreedHandler,
    UpdateBreedHandler,
)
from application.breeds.commands import (
    CreateBreedCommand,
    DeleteBreedCommand,
    ListBreedsQuery,
    SearchBreedsQuery,
    UpdateBreedCommand,
)
from application.breeds.query_handlers import BreedQueryService
from infrastructure.dependencies import (
    get_breed_query_service,
    get_create_breed_handler,
    get_delete_breed_handler,
    get_update_breed_handler,
)
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
    create_breed_handler: CreateBreedHandler = Depends(get_create_breed_handler),
) -> ApiResponse[BreedResponse]:
    command = CreateBreedCommand(name=request.name, description=request.description)
    breed = await create_breed_handler.handle(command)
    return ApiResponse.success(data=BreedResponse.model_validate(breed.model_dump()), message="Breed created successfully")


@router.get(
    "/{breed_id}",
    response_model=ApiResponse[BreedResponse],
    summary="获取品种详情",
)
@handle_exceptions
async def get_breed(
    breed_id: str = Path(..., description="品种ID"),
    breed_query_service: BreedQueryService = Depends(get_breed_query_service),
) -> ApiResponse[BreedResponse]:
    from application.breeds.queries import GetBreedByIdQuery

    query = GetBreedByIdQuery(breed_id=breed_id, include_pets=False)
    breed_details = await breed_query_service.get_breed_details(query)
    return ApiResponse.success(data=BreedResponse.model_validate(breed_details.model_dump()))


@router.put(
    "/{breed_id}",
    response_model=ApiResponse[BreedResponse],
    summary="更新品种",
)
@handle_exceptions
async def update_breed(
    breed_id: str,
    request: UpdateBreedRequest,
    update_breed_handler: UpdateBreedHandler = Depends(get_update_breed_handler),
) -> ApiResponse[BreedResponse]:
    command = UpdateBreedCommand(breed_id=breed_id, name=request.name, description=request.description)
    breed = await update_breed_handler.handle(command)
    return ApiResponse.success(data=BreedResponse.model_validate(breed.model_dump()), message="Breed updated successfully")


@router.delete(
    "/{breed_id}",
    response_model=ApiResponse[dict],
    summary="删除品种",
)
@handle_exceptions
async def delete_breed(
    breed_id: str,
    delete_breed_handler: DeleteBreedHandler = Depends(get_delete_breed_handler),
) -> ApiResponse[dict]:
    command = DeleteBreedCommand(breed_id=breed_id)
    success = await delete_breed_handler.handle(command)
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
    breed_query_service: BreedQueryService = Depends(get_breed_query_service),
) -> PaginatedResponse[BreedResponse]:
    query = ListBreedsQuery(page=page, page_size=page_size, include_deleted=include_deleted)
    result = await breed_query_service.list_breeds(query)
    items = [BreedResponse.model_validate(b.model_dump()) for b in result.breeds]
    return PaginatedResponse.create(items=items, total=result.total, page=page, page_size=page_size)


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
    breed_query_service: BreedQueryService = Depends(get_breed_query_service),
) -> PaginatedResponse[BreedResponse]:
    query = SearchBreedsQuery(
        search_term=q,
        language=language,
        page=page,
        page_size=page_size,
        include_deleted=include_deleted,
    )
    result = await breed_query_service.search_breeds(query)
    items = [BreedResponse.model_validate(b.model_dump()) for b in result.breeds]
    return PaginatedResponse.create(items=items, total=result.total, page=page, page_size=page_size)


