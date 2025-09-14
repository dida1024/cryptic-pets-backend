from fastapi import APIRouter, Depends, status

from application.pet_records.command_handlers import (
    CreatePetRecordHandler,
    DeletePetRecordHandler,
    UpdatePetRecordHandler,
)
from application.pet_records.commands import (
    CreatePetRecordCommand,
    DeletePetRecordCommand,
    UpdatePetRecordCommand,
)
from application.pet_records.queries import (
    GetPetRecordByIdQuery,
    ListPetRecordsQuery,
    SearchPetRecordsQuery,
)
from application.pet_records.query_handlers import PetRecordQueryService
from infrastructure.dependencies import (
    get_create_pet_record_handler,
    get_delete_pet_record_handler,
    get_pet_record_query_service,
    get_update_pet_record_handler,
)
from interfaces.http.base_response import ApiResponse, PaginatedResponse
from interfaces.http.decorators import handle_exceptions
from interfaces.http.v1.schemas.pet_record_schemas import (
    CreateBehaviorRecordRequest,
    CreateEnvironmentalRecordRequest,
    CreateFeedingRecordRequest,
    CreateHealthRecordRequest,
    CreateOtherRecordRequest,
    CreatePetRecordRequest,
    CreateSheddingRecordRequest,
    CreateWeighingRecordRequest,
    PetRecordResponse,
    PetRecordSearchRequest,
    UpdatePetRecordRequest,
)

router = APIRouter(prefix="/pet_records", tags=["pet_records"])


@router.post(
    "",
    response_model=ApiResponse[PetRecordResponse],
    status_code=status.HTTP_201_CREATED,
    summary="创建宠物记录",
    description="创建一个新的宠物记录",
)
@handle_exceptions
async def create_pet_record(
    request: CreatePetRecordRequest,
    create_pet_record_handler: CreatePetRecordHandler = Depends(
        get_create_pet_record_handler
    ),
) -> ApiResponse[PetRecordResponse]:
    """创建宠物记录"""
    command = CreatePetRecordCommand(
        pet_id=request.pet_id,
        creator_id=request.creator_id,
        event_type=request.event_type,
        event_data=request.event_data,
    )
    pet_record = await create_pet_record_handler.handle(command)
    return ApiResponse.success(
        data=PetRecordResponse.model_validate(pet_record.model_dump()),
        message="Pet record created successfully",
    )


# 特定事件类型的创建端点
@router.post(
    "/feeding",
    response_model=ApiResponse[PetRecordResponse],
    status_code=status.HTTP_201_CREATED,
    summary="创建喂食记录",
    description="创建一个新的喂食记录",
)
@handle_exceptions
async def create_feeding_record(
    request: CreateFeedingRecordRequest,
    create_pet_record_handler: CreatePetRecordHandler = Depends(
        get_create_pet_record_handler
    ),
) -> ApiResponse[PetRecordResponse]:
    """创建喂食记录"""
    from domain.pet_records.pet_record_data import FeedingRecordData

    event_data = FeedingRecordData(
        food_name=request.food_name,
        food_amount=request.food_amount,
        food_unit=request.food_unit,
        feeding_method=request.feeding_method,
        description=request.description,
        notes=request.notes,
    )

    command = CreatePetRecordCommand(
        pet_id=request.pet_id,
        creator_id=request.creator_id,
        event_type="FEEDING",
        event_data=event_data.model_dump(),
    )
    pet_record = await create_pet_record_handler.handle(command)
    return ApiResponse.success(
        data=PetRecordResponse.model_validate(pet_record.model_dump()),
        message="Feeding record created successfully",
    )


@router.post(
    "/weighing",
    response_model=ApiResponse[PetRecordResponse],
    status_code=status.HTTP_201_CREATED,
    summary="创建称重记录",
    description="创建一个新的称重记录",
)
@handle_exceptions
async def create_weighing_record(
    request: CreateWeighingRecordRequest,
    create_pet_record_handler: CreatePetRecordHandler = Depends(
        get_create_pet_record_handler
    ),
) -> ApiResponse[PetRecordResponse]:
    """创建称重记录"""
    from domain.pet_records.pet_record_data import WeighingRecordData

    event_data = WeighingRecordData(
        weight=request.weight,
        weight_unit=request.weight_unit,
        scale_type=request.scale_type,
        condition=request.condition,
        description=request.description,
        notes=request.notes,
    )

    command = CreatePetRecordCommand(
        pet_id=request.pet_id,
        creator_id=request.creator_id,
        event_type="WEIGHING",
        event_data=event_data.model_dump(),
    )
    pet_record = await create_pet_record_handler.handle(command)
    return ApiResponse.success(
        data=PetRecordResponse.model_validate(pet_record.model_dump()),
        message="Weighing record created successfully",
    )


@router.post(
    "/shedding",
    response_model=ApiResponse[PetRecordResponse],
    status_code=status.HTTP_201_CREATED,
    summary="创建蜕皮记录",
    description="创建一个新的蜕皮记录",
)
@handle_exceptions
async def create_shedding_record(
    request: CreateSheddingRecordRequest,
    create_pet_record_handler: CreatePetRecordHandler = Depends(
        get_create_pet_record_handler
    ),
) -> ApiResponse[PetRecordResponse]:
    """创建蜕皮记录"""
    from domain.pet_records.pet_record_data import SheddingRecordData

    event_data = SheddingRecordData(
        shedding_area=request.shedding_area,
        shedding_degree=request.shedding_degree,
        shedding_type=request.shedding_type,
        description=request.description,
        notes=request.notes,
    )

    command = CreatePetRecordCommand(
        pet_id=request.pet_id,
        creator_id=request.creator_id,
        event_type="SHEDDING",
        event_data=event_data.model_dump(),
    )
    pet_record = await create_pet_record_handler.handle(command)
    return ApiResponse.success(
        data=PetRecordResponse.model_validate(pet_record.model_dump()),
        message="Shedding record created successfully",
    )


@router.post(
    "/health",
    response_model=ApiResponse[PetRecordResponse],
    status_code=status.HTTP_201_CREATED,
    summary="创建健康记录",
    description="创建一个新的健康记录",
)
@handle_exceptions
async def create_health_record(
    request: CreateHealthRecordRequest,
    create_pet_record_handler: CreatePetRecordHandler = Depends(
        get_create_pet_record_handler
    ),
) -> ApiResponse[PetRecordResponse]:
    """创建健康记录"""
    from domain.pet_records.pet_record_data import HealthRecordData

    event_data = HealthRecordData(
        symptom=request.symptom,
        severity=request.severity,
        treatment=request.treatment,
        vet_visit=request.vet_visit,
        description=request.description,
        notes=request.notes,
    )

    command = CreatePetRecordCommand(
        pet_id=request.pet_id,
        creator_id=request.creator_id,
        event_type="HEALTH_CHECK",
        event_data=event_data.model_dump(),
    )
    pet_record = await create_pet_record_handler.handle(command)
    return ApiResponse.success(
        data=PetRecordResponse.model_validate(pet_record.model_dump()),
        message="Health record created successfully",
    )


@router.post(
    "/behavior",
    response_model=ApiResponse[PetRecordResponse],
    status_code=status.HTTP_201_CREATED,
    summary="创建行为记录",
    description="创建一个新的行为记录",
)
@handle_exceptions
async def create_behavior_record(
    request: CreateBehaviorRecordRequest,
    create_pet_record_handler: CreatePetRecordHandler = Depends(
        get_create_pet_record_handler
    ),
) -> ApiResponse[PetRecordResponse]:
    """创建行为记录"""
    from domain.pet_records.pet_record_data import BehaviorRecordData

    event_data = BehaviorRecordData(
        behavior_type=request.behavior_type,
        duration_minutes=request.duration_minutes,
        intensity=request.intensity,
        description=request.description,
        notes=request.notes,
    )

    command = CreatePetRecordCommand(
        pet_id=request.pet_id,
        creator_id=request.creator_id,
        event_type="BEHAVIOR",
        event_data=event_data.model_dump(),
    )
    pet_record = await create_pet_record_handler.handle(command)
    return ApiResponse.success(
        data=PetRecordResponse.model_validate(pet_record.model_dump()),
        message="Behavior record created successfully",
    )


@router.post(
    "/environment",
    response_model=ApiResponse[PetRecordResponse],
    status_code=status.HTTP_201_CREATED,
    summary="创建环境记录",
    description="创建一个新的环境记录",
)
@handle_exceptions
async def create_environmental_record(
    request: CreateEnvironmentalRecordRequest,
    create_pet_record_handler: CreatePetRecordHandler = Depends(
        get_create_pet_record_handler
    ),
) -> ApiResponse[PetRecordResponse]:
    """创建环境记录"""
    from domain.pet_records.pet_record_data import EnvironmentalRecordData

    event_data = EnvironmentalRecordData(
        temperature=request.temperature,
        humidity=request.humidity,
        light_condition=request.light_condition,
        description=request.description,
        notes=request.notes,
    )

    command = CreatePetRecordCommand(
        pet_id=request.pet_id,
        creator_id=request.creator_id,
        event_type="ENVIRONMENT",
        event_data=event_data.model_dump(),
    )
    pet_record = await create_pet_record_handler.handle(command)
    return ApiResponse.success(
        data=PetRecordResponse.model_validate(pet_record.model_dump()),
        message="Environmental record created successfully",
    )


@router.post(
    "/other",
    response_model=ApiResponse[PetRecordResponse],
    status_code=status.HTTP_201_CREATED,
    summary="创建其他记录",
    description="创建一个新的其他类型记录",
)
@handle_exceptions
async def create_other_record(
    request: CreateOtherRecordRequest,
    create_pet_record_handler: CreatePetRecordHandler = Depends(
        get_create_pet_record_handler
    ),
) -> ApiResponse[PetRecordResponse]:
    """创建其他记录"""
    from domain.pet_records.pet_record_data import OtherRecordData

    event_data = OtherRecordData(
        description=request.description,
        notes=request.notes,
    )

    command = CreatePetRecordCommand(
        pet_id=request.pet_id,
        creator_id=request.creator_id,
        event_type="OTHER",
        event_data=event_data.model_dump(),
    )
    pet_record = await create_pet_record_handler.handle(command)
    return ApiResponse.success(
        data=PetRecordResponse.model_validate(pet_record.model_dump()),
        message="Other record created successfully",
    )


@router.get(
    "/{record_id}",
    response_model=ApiResponse[PetRecordResponse],
    summary="获取宠物记录详情",
    description="根据ID获取宠物记录的详细信息",
)
@handle_exceptions
async def get_pet_record(
    record_id: str,
    query_service: PetRecordQueryService = Depends(get_pet_record_query_service),
) -> ApiResponse[PetRecordResponse]:
    """获取宠物记录详情"""
    query = GetPetRecordByIdQuery(pet_record_id=record_id)
    record_details = await query_service.get_pet_record_details(query)
    return ApiResponse.success(
        data=PetRecordResponse.model_validate(record_details.model_dump()),
        message="Pet record retrieved successfully",
    )


@router.put(
    "/{record_id}",
    response_model=ApiResponse[PetRecordResponse],
    summary="更新宠物记录",
    description="更新指定ID的宠物记录",
)
@handle_exceptions
async def update_pet_record(
    record_id: str,
    request: UpdatePetRecordRequest,
    update_pet_record_handler: UpdatePetRecordHandler = Depends(
        get_update_pet_record_handler
    ),
) -> ApiResponse[PetRecordResponse]:
    """更新宠物记录"""
    command = UpdatePetRecordCommand(
        record_id=record_id,
        event_data=request.event_data,
    )
    pet_record = await update_pet_record_handler.handle(command)
    return ApiResponse.success(
        data=PetRecordResponse.model_validate(pet_record.model_dump()),
        message="Pet record updated successfully",
    )


@router.delete(
    "/{record_id}",
    response_model=ApiResponse[bool],
    summary="删除宠物记录",
    description="删除指定ID的宠物记录（软删除）",
)
@handle_exceptions
async def delete_pet_record(
    record_id: str,
    delete_pet_record_handler: DeletePetRecordHandler = Depends(
        get_delete_pet_record_handler
    ),
) -> ApiResponse[bool]:
    """删除宠物记录"""
    command = DeletePetRecordCommand(record_id=record_id)
    success = await delete_pet_record_handler.handle(command)
    return ApiResponse.success(
        data=success,
        message="Pet record deleted successfully"
        if success
        else "Pet record not found",
    )


@router.get(
    "",
    response_model=PaginatedResponse[PetRecordResponse],
    summary="获取宠物记录列表",
    description="获取宠物记录列表，支持分页和筛选",
)
@handle_exceptions
async def list_pet_records(
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    pet_id: str | None = None,
    event_type: str | None = None,
    creator_id: str | None = None,
    include_deleted: bool = False,
    query_service: PetRecordQueryService = Depends(get_pet_record_query_service),
) -> PaginatedResponse[PetRecordResponse]:
    """获取宠物记录列表"""
    query = ListPetRecordsQuery(
        page=page,
        page_size=page_size,
        search=search,
        pet_id=pet_id,
        event_type=event_type,
        creator_id=creator_id,
        include_deleted=include_deleted,
    )
    result = await query_service.list_pet_records(query)

    # 转换为响应格式
    records = [
        PetRecordResponse.model_validate(record.model_dump())
        for record in result.records
    ]

    return PaginatedResponse.create(
        items=records,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )


@router.post(
    "/search",
    response_model=PaginatedResponse[PetRecordResponse],
    summary="搜索宠物记录",
    description="根据条件搜索宠物记录",
)
@handle_exceptions
async def search_pet_records(
    request: PetRecordSearchRequest,
    query_service: PetRecordQueryService = Depends(get_pet_record_query_service),
) -> PaginatedResponse[PetRecordResponse]:
    """搜索宠物记录"""
    query = SearchPetRecordsQuery(
        search_term=request.search_term,
        pet_id=request.pet_id,
        event_type=request.event_type,
        creator_id=request.creator_id,
        page=request.page,
        page_size=request.page_size,
        include_deleted=request.include_deleted,
    )
    result = await query_service.search_pet_records(query)

    # 转换为响应格式
    records = [
        PetRecordResponse.model_validate(record.model_dump())
        for record in result.records
    ]

    return PaginatedResponse.create(
        items=records,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )


@router.get(
    "/pet/{pet_id}",
    response_model=ApiResponse[list[PetRecordResponse]],
    summary="获取宠物的所有记录",
    description="根据宠物ID获取该宠物的所有记录",
)
@handle_exceptions
async def get_pet_records_by_pet_id(
    pet_id: str,
    query_service: PetRecordQueryService = Depends(get_pet_record_query_service),
) -> ApiResponse[list[PetRecordResponse]]:
    """获取宠物的所有记录"""
    records = await query_service.get_pet_records_by_pet_id(pet_id)
    record_responses = [
        PetRecordResponse.model_validate(record.model_dump()) for record in records
    ]
    return ApiResponse.success(
        data=record_responses,
        message=f"Retrieved {len(record_responses)} records for pet {pet_id}",
    )


@router.get(
    "/creator/{creator_id}",
    response_model=ApiResponse[list[PetRecordResponse]],
    summary="获取创建者的所有记录",
    description="根据创建者ID获取该用户创建的所有记录",
)
@handle_exceptions
async def get_pet_records_by_creator_id(
    creator_id: str,
    query_service: PetRecordQueryService = Depends(get_pet_record_query_service),
) -> ApiResponse[list[PetRecordResponse]]:
    """获取创建者的所有记录"""
    records = await query_service.get_pet_records_by_creator_id(creator_id)
    record_responses = [
        PetRecordResponse.model_validate(record.model_dump()) for record in records
    ]
    return ApiResponse.success(
        data=record_responses,
        message=f"Retrieved {len(record_responses)} records for creator {creator_id}",
    )
