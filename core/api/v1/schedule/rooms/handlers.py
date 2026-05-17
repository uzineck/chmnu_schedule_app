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
    response=ApiResponse[list[RoomSchema]],
    operation_id='get_all_rooms',
    auth=jwt_auth,

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
    response={201: ApiResponse[RoomSchema]},
    operation_id="create_room",
    auth=jwt_auth_room_manager,
)
def create_room(request: HttpRequest, schema: RoomNumberInSchema) -> ApiResponse[RoomSchema]:
    container = get_container()
    use_case: CreateRoomUseCase = container.resolve(CreateRoomUseCase)
    room = use_case.execute(number=schema.number)

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
    use_case: UpdateRoomNumberUseCase = container.resolve(UpdateRoomNumberUseCase)
    room = use_case.execute(room_uuid=room_uuid, new_number=schema.number)

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
    use_case: UpdateRoomDescriptionUseCase = container.resolve(UpdateRoomDescriptionUseCase)
    room = use_case.execute(room_uuid=room_uuid, description=schema.description)

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
    use_case: DeleteRoomUseCase = container.resolve(DeleteRoomUseCase)
    use_case.execute(room_uuid=room_uuid)

    return ApiResponse(
        data=StatusResponse(status="Room deleted successfully"),
    )
