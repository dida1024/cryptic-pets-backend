from fastapi import APIRouter, Depends, Path, Query, status

from application.pets.commands import (
    CreatePetCommand,
    DeletePetCommand,
    TransferPetOwnershipCommand,
    UpdatePetCommand,
)
from application.pets.command_handlers import (
    CreatePetHandler,
    DeletePetHandler,
    TransferPetOwnershipHandler,
    UpdatePetHandler,
)
from application.pets.queries import (
    GetPetByIdQuery,
    ListPetsByOwnerQuery,
    SearchPetsQuery,
)
from application.pets.query_handlers import PetQueryService
from infrastructure.dependencies import (
    get_create_pet_handler,
    get_delete_pet_handler,
    get_pet_query_service,
    get_transfer_pet_ownership_handler,
    get_update_pet_handler,
)
from interfaces.http.base_response import ApiResponse, PaginatedResponse
from interfaces.http.decorators import handle_exceptions
from interfaces.http.v1.schemas.pet_schemas import (
    CreatePetRequest,
    PetDetailResponse,
    PetResponse,
    PetSummaryResponse,
    TransferPetOwnershipRequest,
    UpdatePetRequest,
)

router = APIRouter(prefix="/pets", tags=["pets"])


@router.post(
    "",
    response_model=ApiResponse[PetResponse],
    status_code=status.HTTP_201_CREATED,
    summary="创建宠物",
    description="创建新宠物",
)
@handle_exceptions
async def create_pet(
    request: CreatePetRequest,
    handler: CreatePetHandler = Depends(get_create_pet_handler),
) -> ApiResponse[PetResponse]:
    """创建宠物"""
    command = CreatePetCommand(
        name=request.name,
        owner_id=request.owner_id,
        breed_id=request.breed_id,
        birth_date=request.birth_date,
        gender=request.gender,
        description=request.description,
        morphology_id=request.morphology_id,
        extra_gene_list=request.extra_gene_list,
    )
    pet = await handler.handle(command)
    return ApiResponse.success(
        data=PetResponse.model_validate(pet.model_dump()),
        message="Pet created successfully",
    )


@router.get(
    "",
    response_model=PaginatedResponse[PetSummaryResponse],
    summary="搜索宠物",
    description="搜索宠物，支持多种过滤条件",
)
@handle_exceptions
async def search_pets(
    search_term: str | None = Query(None, description="搜索关键字"),
    owner_id: str | None = Query(None, description="按主人ID过滤"),
    breed_id: str | None = Query(None, description="按品种ID过滤"),
    morphology_id: str | None = Query(None, description="按形态学ID过滤"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    query_service: PetQueryService = Depends(get_pet_query_service),
) -> PaginatedResponse[PetSummaryResponse]:
    """搜索宠物"""
    query = SearchPetsQuery(
        search_term=search_term,
        owner_id=owner_id,
        breed_id=breed_id,
        morphology_id=morphology_id,
        page=page,
        page_size=page_size,
    )
    result = await query_service.search_pets(query)
    items = [PetSummaryResponse.model_validate(pet.model_dump()) for pet in result.pets]
    return PaginatedResponse.create(
        items=items,
        total=result.total_count,
        page=result.page,
        page_size=result.page_size,
    )


@router.get(
    "/owner/{owner_id}",
    response_model=PaginatedResponse[PetSummaryResponse],
    summary="获取用户的宠物",
    description="获取指定用户的所有宠物",
)
@handle_exceptions
async def list_pets_by_owner(
    owner_id: str = Path(..., description="用户ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    query_service: PetQueryService = Depends(get_pet_query_service),
) -> PaginatedResponse[PetSummaryResponse]:
    """获取用户的宠物"""
    query = ListPetsByOwnerQuery(
        owner_id=owner_id,
        page=page,
        page_size=page_size,
    )
    result = await query_service.list_pets_by_owner(query)
    items = [PetSummaryResponse.model_validate(pet.model_dump()) for pet in result.pets]
    return PaginatedResponse.create(
        items=items,
        total=result.total_count,
        page=result.page,
        page_size=result.page_size,
    )


@router.get(
    "/{pet_id}",
    response_model=ApiResponse[PetDetailResponse],
    summary="获取宠物详情",
    description="根据宠物ID获取宠物详情",
)
@handle_exceptions
async def get_pet(
    pet_id: str = Path(..., description="宠物ID"),
    include_owner: bool = Query(True, description="是否包含主人信息"),
    include_breed: bool = Query(True, description="是否包含品种信息"),
    include_morphology: bool = Query(False, description="是否包含形态学信息"),
    query_service: PetQueryService = Depends(get_pet_query_service),
) -> ApiResponse[PetDetailResponse]:
    """获取宠物详情"""
    query = GetPetByIdQuery(
        pet_id=pet_id,
        include_owner=include_owner,
        include_breed=include_breed,
        include_morphology=include_morphology,
    )
    pet = await query_service.get_pet_details(query)
    return ApiResponse.success(data=PetDetailResponse.model_validate(pet.model_dump()))


@router.put(
    "/{pet_id}",
    response_model=ApiResponse[PetResponse],
    summary="更新宠物",
    description="更新宠物信息",
)
@handle_exceptions
async def update_pet(
    pet_id: str = Path(..., description="宠物ID"),
    request: UpdatePetRequest = None,
    handler: UpdatePetHandler = Depends(get_update_pet_handler),
) -> ApiResponse[PetResponse]:
    """更新宠物"""
    command = UpdatePetCommand(
        pet_id=pet_id,
        name=request.name if request else None,
        owner_id=request.owner_id if request else None,
        breed_id=request.breed_id if request else None,
        birth_date=request.birth_date if request else None,
        gender=request.gender if request else None,
        description=request.description if request else None,
        morphology_id=request.morphology_id if request else None,
    )
    pet = await handler.handle(command)
    return ApiResponse.success(
        data=PetResponse.model_validate(pet.model_dump()),
        message="Pet updated successfully",
    )


@router.post(
    "/{pet_id}/transfer",
    response_model=ApiResponse[PetResponse],
    summary="转移宠物所有权",
    description="将宠物转移给新主人",
)
@handle_exceptions
async def transfer_pet_ownership(
    pet_id: str = Path(..., description="宠物ID"),
    request: TransferPetOwnershipRequest = None,
    handler: TransferPetOwnershipHandler = Depends(get_transfer_pet_ownership_handler),
) -> ApiResponse[PetResponse]:
    """转移宠物所有权"""
    command = TransferPetOwnershipCommand(
        pet_id=pet_id,
        new_owner_id=request.new_owner_id,
        current_user_id=request.current_user_id,
    )
    pet = await handler.handle(command)
    return ApiResponse.success(
        data=PetResponse.model_validate(pet.model_dump()),
        message="Pet ownership transferred successfully",
    )


@router.delete(
    "/{pet_id}",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="删除宠物",
    description="删除宠物（软删除）",
)
@handle_exceptions
async def delete_pet(
    pet_id: str = Path(..., description="宠物ID"),
    handler: DeletePetHandler = Depends(get_delete_pet_handler),
) -> ApiResponse[dict]:
    """删除宠物"""
    command = DeletePetCommand(pet_id=pet_id)
    success = await handler.handle(command)
    return ApiResponse.success(data={"deleted": success}, message="Pet deleted successfully")