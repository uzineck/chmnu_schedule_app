from django.http import HttpRequest
from ninja import (
    Query,
    Router,
)
from ninja.errors import HttpError

from core.api.filters import (
    PaginationIn,
    PaginationOut,
    SearchFilter,
)
from core.api.schemas import (
    ApiResponse,
    ListPaginatedResponse,
    StatusResponse,
)
from core.api.v1.schedule.rooms.schemas import (
    RoomDescriptionInSchema,
    RoomNumberInSchema,
    RoomSchema,
)
from core.apps.common.authentication.ninja_auth import (
    jwt_auth,
    jwt_auth_room_manager,
)
from core.apps.common.cache.service import BaseCacheService
from core.apps.common.cache.timeouts import Timeout
from core.apps.common.exceptions import ServiceException
from core.apps.common.filters import SearchFilter as SearchFilterEntity
from core.apps.schedule.use_cases.room.create import CreateRoomUseCase
from core.apps.schedule.use_cases.room.delete import DeleteRoomUseCase
from core.apps.schedule.use_cases.room.get_all import GetAllRoomsUseCase
from core.apps.schedule.use_cases.room.get_list import GetRoomListUseCase
from core.apps.schedule.use_cases.room.update_description import UpdateRoomDescriptionUseCase
from core.apps.schedule.use_cases.room.update_number import UpdateRoomNumberUseCase
from core.project.containers.containers import get_container


router = Router(tags=["Rooms"])


@router.get(
    'all',
    response=ApiResponse[list[RoomSchema]],
    operation_id='get_all_rooms',
    auth=jwt_auth,

)
def get_all_rooms(request: HttpRequest) -> ApiResponse[list[RoomSchema]]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: GetAllRoomsUseCase = container.resolve(GetAllRoomsUseCase)
    try:
        cache_key = cache_service.generate_cache_key(
            model_prefix="room",
            func_prefix="all",
        )
        items = cache_service.get_cache_value(key=cache_key)
        if not items:
            items = [RoomSchema.from_entity(obj) for obj in use_case.execute()]
            cache_service.set_cache(key=cache_key, value=items, timeout=Timeout.MONTH)

    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )
    return ApiResponse(
        data=items,
    )


@router.get(
    "",
    response=ApiResponse[ListPaginatedResponse[RoomSchema]],
    operation_id="get_room_list",
    auth=jwt_auth,
)
def get_room_list(
    request: HttpRequest,
    filters: Query[SearchFilter],
    pagination_in: Query[PaginationIn],
) -> ApiResponse[ListPaginatedResponse[RoomSchema]]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: GetRoomListUseCase = container.resolve(GetRoomListUseCase)
    try:
        cache_key = cache_service.generate_cache_key(
            model_prefix="room",
            func_prefix="list",
            filters=filters,
            pagination_in=pagination_in,
        )
        items = cache_service.get_cache_value(key=cache_key)
        if not items:
            item_list, item_count = use_case.execute(
                filters=SearchFilterEntity(search=filters.search),
                pagination=pagination_in,
            )
            pagination_out = PaginationOut(
                offset=pagination_in.offset,
                limit=pagination_in.limit,
                total=item_count,
            )
            items = item_list, pagination_out
            cache_service.set_cache(key=cache_key, value=items, timeout=Timeout.DAY)

        item_list, pagination_out = items
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )

    return ApiResponse(
        data=ListPaginatedResponse(
            items=[RoomSchema.from_entity(obj) for obj in item_list],
            pagination=pagination_out,
        ),
    )


@router.post(
    "",
    response={201: ApiResponse[RoomSchema]},
    operation_id="create_room",
    auth=jwt_auth_room_manager,
)
def create_room(request: HttpRequest, schema: RoomNumberInSchema) -> ApiResponse[RoomSchema]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: CreateRoomUseCase = container.resolve(CreateRoomUseCase)
    try:
        room = use_case.execute(number=schema.number)
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="room",
                    func_prefix="all",
                ),
                cache_service.generate_cache_key(
                    model_prefix="room",
                    func_prefix="list",
                    filters="*",
                    pagination_in="*",
                ),
            ],
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )

    return ApiResponse(
        data=RoomSchema.from_entity(entity=room),
    )


@router.patch(
    "{room_uuid}/update_number",
    response=ApiResponse[RoomSchema],
    operation_id="update_room_number",
    auth=jwt_auth_room_manager,
)
def update_room_number(
    request: HttpRequest,
    room_uuid: str,
    schema: RoomNumberInSchema,
) -> ApiResponse[RoomSchema]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: UpdateRoomNumberUseCase = container.resolve(UpdateRoomNumberUseCase)
    try:
        room = use_case.execute(room_uuid=room_uuid, new_number=schema.number)
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="room",
                    func_prefix="all",
                ),
                cache_service.generate_cache_key(
                    model_prefix="room",
                    func_prefix="list",
                    filters="*",
                    pagination_in="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="group",
                    identifier="*",
                    func_prefix="lessons",
                    filters="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="teacher",
                    identifier="*",
                    func_prefix="lessons",
                    filters="*",
                ),
            ],
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )

    return ApiResponse(
        data=RoomSchema.from_entity(entity=room),
    )


@router.patch(
    "{room_uuid}/update_description",
    response=ApiResponse[RoomSchema],
    operation_id="update_room_description",
    auth=jwt_auth_room_manager,
)
def update_room_description(
    request: HttpRequest,
    room_uuid: str,
    schema: RoomDescriptionInSchema,
) -> ApiResponse[RoomSchema]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: UpdateRoomDescriptionUseCase = container.resolve(UpdateRoomDescriptionUseCase)
    try:
        room = use_case.execute(room_uuid=room_uuid, description=schema.description)
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="room",
                    func_prefix="all",
                ),
                cache_service.generate_cache_key(
                    model_prefix="room",
                    func_prefix="list",
                    filters="*",
                    pagination_in="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="group",
                    identifier="*",
                    func_prefix="lessons",
                    filters="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="teacher",
                    identifier="*",
                    func_prefix="lessons",
                    filters="*",
                ),
            ],
        )

    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )

    return ApiResponse(
        data=RoomSchema.from_entity(entity=room),
    )


@router.delete(
    "{room_uuid}",
    response=ApiResponse[StatusResponse],
    operation_id="delete_room",
    auth=jwt_auth_room_manager,
)
def delete_room(
    request: HttpRequest,
    room_uuid: str,
) -> ApiResponse[StatusResponse]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: DeleteRoomUseCase = container.resolve(DeleteRoomUseCase)
    try:
        use_case.execute(room_uuid=room_uuid)
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="room",
                    func_prefix="all",
                ),
                cache_service.generate_cache_key(
                    model_prefix="room",
                    func_prefix="list",
                    filters="*",
                    pagination_in="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="group",
                    identifier="*",
                    func_prefix="lessons",
                    filters="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="teacher",
                    identifier="*",
                    func_prefix="lessons",
                    filters="*",
                ),
            ],
        )

    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )

    return ApiResponse(
        data=StatusResponse(status="Room deleted successfully"),
    )
