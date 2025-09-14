from fastapi import APIRouter, Depends, Query, status

from application.pets.command_handlers import CreatePetHandler
from application.pets.commands import CreatePetCommand
from application.pets.query_handlers import PetQueryService
from application.users.command_handlers import (
    CreateUserHandler,
    DeleteUserHandler,
    UpdatePasswordHandler,
    UpdateUserHandler,
)
from application.users.commands import (
    CreateUserCommand,
    DeleteUserCommand,
    ListUsersQuery,
    UpdatePasswordCommand,
    UpdateUserCommand,
)
from application.users.query_handlers import UserQueryService
from domain.users.exceptions import UserNotFoundError
from infrastructure.dependencies import (
    get_create_pet_handler,
    get_create_user_handler,
    get_delete_user_handler,
    get_pet_query_service,
    get_update_password_handler,
    get_update_user_handler,
    get_user_query_service,
)
from interfaces.http.base_response import ApiResponse, PaginatedResponse
from interfaces.http.decorators import handle_exceptions
from interfaces.http.v1.schemas.pet_schemas import CreatePetRequest, PetResponse
from interfaces.http.v1.schemas.user_schemas import (
    CreateUserRequest,
    PasswordUpdateRequest,
    UpdateUserRequest,
    UserResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="创建用户",
    description="创建新用户账户",
)
@handle_exceptions
async def create_user(
    request: CreateUserRequest,
    create_user_handler: CreateUserHandler = Depends(get_create_user_handler),
) -> ApiResponse[UserResponse]:
    """创建用户"""
    command = CreateUserCommand(
        username=request.username,
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        user_type=request.user_type,
        is_active=request.is_active,
    )

    user = await create_user_handler.handle(command)
    user_response = UserResponse.model_validate(user.model_dump())

    return ApiResponse.success(data=user_response, message="User created successfully")


@router.get(
    "/{user_id}",
    response_model=ApiResponse[UserResponse],
    summary="获取用户详情",
    description="根据用户ID获取用户详情",
)
@handle_exceptions
async def get_user(
    user_id: str,
    user_query_service: UserQueryService = Depends(get_user_query_service),
) -> ApiResponse[UserResponse]:
    """获取用户详情"""
    from application.users.queries import GetUserByIdQuery

    query = GetUserByIdQuery(user_id=user_id, include_profile=False)
    user_details = await user_query_service.get_user_details(query)

    # 转换为响应模型
    user_response = UserResponse.model_validate(user_details.model_dump())

    return ApiResponse.success(data=user_response)


@router.put(
    "/{user_id}",
    response_model=ApiResponse[UserResponse],
    summary="更新用户",
    description="更新用户信息",
)
@handle_exceptions
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    update_user_handler: UpdateUserHandler = Depends(get_update_user_handler),
) -> ApiResponse[UserResponse]:
    """更新用户"""
    command = UpdateUserCommand(
        user_id=user_id,
        username=request.username,
        email=request.email,
        full_name=request.full_name,
        user_type=request.user_type,
        is_active=request.is_active,
    )

    user = await update_user_handler.handle(command)
    user_response = UserResponse.model_validate(user.model_dump())

    return ApiResponse.success(data=user_response, message="User updated successfully")


@router.patch(
    "/{user_id}/password",
    response_model=ApiResponse[UserResponse],
    summary="更新用户密码",
    description="更新用户密码",
)
@handle_exceptions
async def update_password(
    user_id: str,
    request: PasswordUpdateRequest,
    update_password_handler: UpdatePasswordHandler = Depends(get_update_password_handler),
) -> ApiResponse[UserResponse]:
    """更新用户密码"""
    command = UpdatePasswordCommand(
        user_id=user_id,
        current_password=request.current_password,
        new_password=request.new_password,
    )

    user = await update_password_handler.handle(command)
    user_response = UserResponse.model_validate(user.model_dump())

    return ApiResponse.success(
        data=user_response, message="Password updated successfully"
    )


@router.delete(
    "/{user_id}",
    response_model=ApiResponse[dict],
    summary="删除用户",
    description="删除用户（软删除）",
)
@handle_exceptions
async def delete_user(
    user_id: str,
    delete_user_handler: DeleteUserHandler = Depends(get_delete_user_handler),
) -> ApiResponse[dict]:
    """删除用户"""
    command = DeleteUserCommand(user_id=user_id)
    success = await delete_user_handler.handle(command)

    if success:
        return ApiResponse.success(
            data={"deleted": True}, message="User deleted successfully"
        )
    else:
        raise UserNotFoundError


@router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
    summary="获取用户列表",
    description="获取用户列表，支持搜索和过滤",
)
@handle_exceptions
async def list_all(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: str = Query(None, description="搜索关键字（用户名或邮箱）"),
    user_type: str = Query(None, description="用户类型过滤"),
    is_active: bool = Query(None, description="激活状态过滤"),
    include_deleted: bool = Query(False, description="是否包含已删除用户"),
    user_query_service: UserQueryService = Depends(get_user_query_service),
) -> PaginatedResponse[UserResponse]:
    """获取用户列表"""
    from domain.users.value_objects import UserTypeEnum

    # 转换用户类型字符串为枚举
    user_type_enum = None
    if user_type:
        try:
            user_type_enum = UserTypeEnum(user_type)
        except ValueError:
            # 如果转换失败，保持为 None
            pass

    query = ListUsersQuery(
        page=page,
        page_size=page_size,
        search=search,
        user_type=user_type_enum,
        is_active=is_active,
        include_deleted=include_deleted,
    )

    result = await user_query_service.list_users(query)

    # 转换为响应模型
    user_responses = [UserResponse.model_validate(user.model_dump()) for user in result.users]

    return PaginatedResponse.create(
        items=user_responses, total=result.total, page=page, page_size=page_size
    )


# about pet ->
@router.post(
    "/{user_id}/pets",
    response_model=ApiResponse[PetResponse],
    status_code=status.HTTP_201_CREATED,
    summary="为用户创建宠物",
    description="为指定用户创建新的宠物记录",
)
@handle_exceptions
async def create_user_pet(
    user_id: str,
    request: CreatePetRequest,
    create_pet_handler: CreatePetHandler = Depends(get_create_pet_handler),
) -> ApiResponse[PetResponse]:
    """为用户创建宠物"""
    command = CreatePetCommand(
        name=request.name,
        owner_id=user_id,
        breed_id=request.breed_id,
        birth_date=request.birth_date,
        gender=request.gender,
        description=request.description,
    )

    pet = await create_pet_handler.handle(command)
    pet_response = PetResponse.model_validate(pet.model_dump())

    return ApiResponse.success(data=pet_response, message="Pet created successfully")


@router.get("/{user_id}/pets", response_model=PaginatedResponse[PetResponse])
async def get_user_pets(
    user_id: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: str = Query(None, description="搜索关键字（宠物名）"),
    pet_query_service: PetQueryService = Depends(get_pet_query_service),
) -> PaginatedResponse[PetResponse]:
    """获取用户宠物列表"""
    from application.pets.queries import SearchPetsQuery

    query = SearchPetsQuery(
        owner_id=user_id, search_term=search, page=page, page_size=page_size
    )
    result = await pet_query_service.search_pets(query)

    pet_responses = [PetResponse.model_validate(pet.model_dump()) for pet in result.pets]
    return PaginatedResponse.create(
        items=pet_responses,
        total=result.total_count,
        page=page,
        page_size=page_size,
    )
