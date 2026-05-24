from django.http import HttpRequest
from ninja import (
    Query,
    Router,
)

from core.api.filters import (
    PaginationIn,
    PaginationOut,
    SearchFilter,
)
from core.api.schemas import (
    ApiErrorResponse,
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
    response={
        200: ApiResponse[list[RoomSchema]],
        401: ApiErrorResponse,
    },
    operation_id='get_all_rooms',
    auth=jwt_auth,
    summary="List every active room",
    description=(
        "Returns the full collection of active rooms — no pagination, no filtering. Intended for "
        "dropdowns. Use `get_room_list` for paginated / searchable access."
    ),
)
def get_all_rooms(request: HttpRequest) -> ApiResponse[list[RoomSchema]]:
    container = get_container()
    use_case: GetAllRoomsUseCase = container.resolve(GetAllRoomsUseCase)
    items = [RoomSchema.from_entity(obj) for obj in use_case.execute()]
    return ApiResponse(
        data=items,
    )


@router.get(
    "",
    response={
        200: ApiResponse[ListPaginatedResponse[RoomSchema]],
        401: ApiErrorResponse,
    },
    operation_id="get_room_list",
    auth=jwt_auth,
    summary="Search and paginate rooms",
    description="Returns a paginated list of active rooms; `search` matches against the room number and description.",
)
def get_room_list(
    request: HttpRequest,
    filters: Query[SearchFilter],
    pagination_in: Query[PaginationIn],
) -> ApiResponse[ListPaginatedResponse[RoomSchema]]:
    container = get_container()
    use_case: GetRoomListUseCase = container.resolve(GetRoomListUseCase)
    item_list, item_count = use_case.execute(
        filters=SearchFilterEntity(search=filters.search),
        pagination_in=pagination_in,
    )
    pagination_out = PaginationOut(
        offset=pagination_in.offset,
        limit=pagination_in.limit,
        total=item_count,
    )

    return ApiResponse(
        data=ListPaginatedResponse(
            items=[RoomSchema.from_entity(obj) for obj in item_list],
            pagination=pagination_out,
        ),
    )


@router.post(
    "",
    response={
        201: ApiResponse[RoomSchema],
        400: ApiErrorResponse,
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        409: ApiErrorResponse,
    },
    operation_id="create_room",
    auth=jwt_auth_room_manager,
    summary="Create a room",
    description=(
        "Registers a new room. `number` must be unique across active rooms. Description is set "
        "via a separate endpoint. Requires ADMIN or ROOM_MANAGER role."
    ),
)
def create_room(
        request: HttpRequest,
        schema: RoomNumberInSchema,
) -> tuple[int, ApiResponse[RoomSchema]]:
    container = get_container()
    use_case: CreateRoomUseCase = container.resolve(CreateRoomUseCase)
    room = use_case.execute(number=schema.number)

    return 201, ApiResponse(
        data=RoomSchema.from_entity(entity=room),
    )


@router.patch(
    "{room_uuid}/update_number",
    response={
        200: ApiResponse[RoomSchema],
        400: ApiErrorResponse,
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
        409: ApiErrorResponse,
    },
    operation_id="update_room_number",
    auth=jwt_auth_room_manager,
    summary="Change a room's number",
    description="Renames a room. Returns 409 if the new number is already taken by another active room.",
)
def update_room_number(
    request: HttpRequest,
    room_uuid: str,
    schema: RoomNumberInSchema,
) -> ApiResponse[RoomSchema]:
    container = get_container()
    use_case: UpdateRoomNumberUseCase = container.resolve(UpdateRoomNumberUseCase)
    room = use_case.execute(room_uuid=room_uuid, new_number=schema.number)

    return ApiResponse(
        data=RoomSchema.from_entity(entity=room),
    )


@router.patch(
    "{room_uuid}/update_description",
    response={
        200: ApiResponse[RoomSchema],
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
    },
    operation_id="update_room_description",
    auth=jwt_auth_room_manager,
    summary="Change a room's description",
    description="Updates the free-text description (e.g. 'computer lab, 25 stations'). Number is left untouched.",
)
def update_room_description(
    request: HttpRequest,
    room_uuid: str,
    schema: RoomDescriptionInSchema,
) -> ApiResponse[RoomSchema]:
    container = get_container()
    use_case: UpdateRoomDescriptionUseCase = container.resolve(UpdateRoomDescriptionUseCase)
    room = use_case.execute(room_uuid=room_uuid, description=schema.description)

    return ApiResponse(
        data=RoomSchema.from_entity(entity=room),
    )


@router.delete(
    "{room_uuid}",
    response={
        200: ApiResponse[StatusResponse],
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
        409: ApiErrorResponse,
    },
    operation_id="delete_room",
    auth=jwt_auth_room_manager,
    summary="Soft-delete a room",
    description="Marks the room inactive. Returns 409 if the room is still referenced by any active lesson.",
)
def delete_room(
    request: HttpRequest,
    room_uuid: str,
) -> ApiResponse[StatusResponse]:
    container = get_container()
    use_case: DeleteRoomUseCase = container.resolve(DeleteRoomUseCase)
    use_case.execute(room_uuid=room_uuid)

    return ApiResponse(
        data=StatusResponse(status="Room deleted successfully"),
    )
