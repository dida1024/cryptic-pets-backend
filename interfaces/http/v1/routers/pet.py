from fastapi import APIRouter, Depends, Path, Query, status

from application.pets.commands import DeletePetCommand, ListPetsQuery, UpdatePetCommand
from application.pets.handlers import PetService
from infrastructure.dependencies import get_pet_service
from interfaces.http.base_response import ApiResponse, PaginatedResponse
from interfaces.http.decorators import handle_exceptions
from interfaces.http.v1.schemas.pet_schemas import PetResponse, UpdatePetRequest

router = APIRouter(prefix="/pets", tags=["pets"])


@router.get(
    "",
    response_model=PaginatedResponse[PetResponse],
    summary="获取宠物列表",
    description="获取宠物列表，支持搜索和过滤",
)
@handle_exceptions
async def list_pets(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: str | None = Query(None, description="搜索关键字（宠物名）"),
    owner_id: str | None = Query(None, description="按用户ID过滤"),
    pet_service: PetService = Depends(get_pet_service),
) -> PaginatedResponse[PetResponse]:
    query = ListPetsQuery(page=page, page_size=page_size, search=search, owner_id=owner_id)
    pets, total = await pet_service.list_all(query)
    items = [PetResponse.model_validate(p.model_dump()) for p in pets]
    return PaginatedResponse.create(items=items, total=total, page=page, page_size=page_size)


@router.get(
    "/{pet_id}",
    response_model=ApiResponse[PetResponse],
    summary="获取宠物详情",
    description="根据宠物ID获取宠物详情",
)
@handle_exceptions
async def get_pet(
    pet_id: str = Path(..., description="宠物ID"),
    pet_service: PetService = Depends(get_pet_service),
) -> ApiResponse[PetResponse]:
    pet = await pet_service.get_pet_by_id(pet_id)
    return ApiResponse.success(data=PetResponse.model_validate(pet.model_dump()))


@router.put(
    "/{pet_id}",
    response_model=ApiResponse[PetResponse],
    summary="更新宠物",
    description="更新宠物信息",
)
@handle_exceptions
async def update_pet(
    pet_id: str,
    request: UpdatePetRequest,
    pet_service: PetService = Depends(get_pet_service),
) -> ApiResponse[PetResponse]:
    command = UpdatePetCommand(
        pet_id=pet_id,
        name=request.name,
        breed_id=request.breed_id,
        birth_date=request.birth_date,
        gender=request.gender,
    )
    pet = await pet_service.update_pet(command)
    return ApiResponse.success(data=PetResponse.model_validate(pet.model_dump()), message="Pet updated successfully")


@router.delete(
    "/{pet_id}",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="删除宠物",
    description="删除宠物（软删除）",
)
@handle_exceptions
async def delete_pet(
    pet_id: str,
    pet_service: PetService = Depends(get_pet_service),
) -> ApiResponse[dict]:
    success = await pet_service.delete_pet(DeletePetCommand(pet_id=pet_id))
    return ApiResponse.success(data={"deleted": success})
