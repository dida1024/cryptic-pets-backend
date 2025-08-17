from fastapi import APIRouter, Depends, Query, status

from application.users.commands import (
    CreateUserCommand,
    DeleteUserCommand,
    ListUsersQuery,
    UpdatePasswordCommand,
    UpdateUserCommand,
)
from application.users.handlers import UserService
from domain.users.exceptions import UserNotFoundError
from infrastructure.persistence.postgres.repositories.user_repository import (
    PostgreSQLUserRepository,
)
from interfaces.http.base_response import ApiResponse, PaginatedResponse
from interfaces.http.decorators import handle_exceptions
from interfaces.http.v1.schemas.user_schemas import (
    CreateUserRequest,
    PasswordUpdateRequest,
    UpdateUserRequest,
    UserResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


async def get_user_service() -> UserService:
    """获取用户服务实例"""
    user_repository = PostgreSQLUserRepository()
    return UserService(user_repository)


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
    user_service: UserService = Depends(get_user_service),
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

    user = await user_service.create_user(command)
    user_response = UserResponse.model_validate(user.model_dump())

    return ApiResponse.success(
        data=user_response,
        message="User created successfully"
    )


@router.get(
    "/{user_id}",
    response_model=ApiResponse[UserResponse],
    summary="获取用户详情",
    description="根据用户ID获取用户详情",
)
@handle_exceptions
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[UserResponse]:
    """获取用户详情"""
    user = await user_service.get_user_by_id(user_id)
    user_response = UserResponse.model_validate(user.model_dump())

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
    user_service: UserService = Depends(get_user_service),
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

    user = await user_service.update_user(command)
    user_response = UserResponse.model_validate(user.model_dump())

    return ApiResponse.success(
        data=user_response,
        message="User updated successfully"
    )


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
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[UserResponse]:
    """更新用户密码"""
    command = UpdatePasswordCommand(
        user_id=user_id,
        current_password=request.current_password,
        new_password=request.new_password,
    )

    user = await user_service.update_password(command)
    user_response = UserResponse.model_validate(user.model_dump())

    return ApiResponse.success(
        data=user_response,
        message="Password updated successfully"
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
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[dict]:
    """删除用户"""
    command = DeleteUserCommand(user_id=user_id)
    success = await user_service.delete_user(command)

    if success:
        return ApiResponse.success(
            data={"deleted": True},
            message="User deleted successfully"
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
async def list_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: str = Query(None, description="搜索关键字（用户名或邮箱）"),
    user_type: str = Query(None, description="用户类型过滤"),
    is_active: bool = Query(None, description="激活状态过滤"),
    include_deleted: bool = Query(False, description="是否包含已删除用户"),
    user_service: UserService = Depends(get_user_service),
) -> PaginatedResponse[UserResponse]:
    """获取用户列表"""
    query = ListUsersQuery(
        page=page,
        page_size=page_size,
        search=search,
        user_type=user_type,
        is_active=is_active,
        include_deleted=include_deleted,
    )

    users, total = await user_service.list_users(query)

    # 转换为响应模型
    user_responses = [
        UserResponse.model_validate(user.model_dump()) for user in users
    ]

    return PaginatedResponse.create(
        items=user_responses,
        total=total,
        page=page,
        page_size=page_size
    )
