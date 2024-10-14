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
)
from core.api.v1.schedule.rooms.schemas import (
    RoomDescriptionInSchema,
    RoomNumberInSchema,
    RoomSchema,
)
from core.apps.common.authentication.bearer import jwt_bearer_admin
from core.apps.common.exceptions import ServiceException
from core.apps.common.filters import SearchFilter as SearchFilterEntity
from core.apps.schedule.use_cases.room.create import CreateRoomUseCase
from core.apps.schedule.use_cases.room.get_all import GetAllRoomsUseCase
from core.apps.schedule.use_cases.room.get_list import GetRoomListUseCase
from core.apps.schedule.use_cases.room.update_description import UpdateRoomDescriptionUseCase
from core.apps.schedule.use_cases.room.update_number import UpdateRoomNumberUseCase
from core.project.containers.containers import get_container


router = Router(tags=["Rooms"])


@router.get(
    'all',
    response=ApiResponse,
    operation_id='get_all_rooms',

)
def get_all_rooms(request: HttpRequest) -> ApiResponse:
    container = get_container()
    use_case: GetAllRoomsUseCase = container.resolve(GetAllRoomsUseCase)
    rooms = use_case.execute()
    items = [RoomSchema.from_entity(obj) for obj in rooms]

    return ApiResponse(
        data=items,
    )


@router.get(
    "",
    response=ApiResponse[ListPaginatedResponse[RoomSchema]],
    operation_id="get_room_list",
)
def get_room_list(
    request: HttpRequest,
    filters: Query[SearchFilter],
    pagination_in: Query[PaginationIn],
) -> ApiResponse[ListPaginatedResponse[RoomSchema]]:
    container = get_container()
    use_case: GetRoomListUseCase = container.resolve(GetRoomListUseCase)
    try:
        room_list, room_count = use_case.execute(
            filters=SearchFilterEntity(search=filters.search),
            pagination=pagination_in,
        )

        items = [RoomSchema.from_entity(obj) for obj in room_list]
        pagination_out = PaginationOut(
            offset=pagination_in.offset,
            limit=pagination_in.limit,
            total=room_count,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=ListPaginatedResponse(
            items=items,
            pagination=pagination_out,
        ),
    )


@router.post(
    "",
    response=ApiResponse[RoomSchema],
    operation_id="create_room",
    auth=jwt_bearer_admin,
)
def create_room(request: HttpRequest, schema: RoomNumberInSchema) -> ApiResponse[RoomSchema]:
    container = get_container()
    use_case: CreateRoomUseCase = container.resolve(CreateRoomUseCase)
    try:
        room = use_case.execute(number=schema.number)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=RoomSchema.from_entity(entity=room),
    )


@router.patch(
    "{room_uuid}/update_number",
    response=ApiResponse[RoomSchema],
    operation_id="update_room_number",
    auth=jwt_bearer_admin,
)
def update_room_number(
    request: HttpRequest,
    room_uuid: str,
    schema: RoomNumberInSchema,
) -> ApiResponse[RoomSchema]:
    container = get_container()
    use_case: UpdateRoomNumberUseCase = container.resolve(UpdateRoomNumberUseCase)
    try:
        room = use_case.execute(room_uuid=room_uuid, new_number=schema.number)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=RoomSchema.from_entity(entity=room),
    )


@router.patch(
    "{room_uuid}/update_description",
    response=ApiResponse[RoomSchema],
    operation_id="update_room_description",
    auth=jwt_bearer_admin,
)
def update_room_description(
    request: HttpRequest,
    room_uuid: str,
    schema: RoomDescriptionInSchema,
) -> ApiResponse[RoomSchema]:
    container = get_container()
    use_case: UpdateRoomDescriptionUseCase = container.resolve(UpdateRoomDescriptionUseCase)
    try:
        room = use_case.execute(room_uuid=room_uuid, description=schema.description)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=RoomSchema.from_entity(entity=room),
    )
