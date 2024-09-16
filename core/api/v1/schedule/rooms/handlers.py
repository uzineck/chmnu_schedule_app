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
    RoomDescriptionUpdateInSchema,
    RoomNumberInSchema,
    RoomNumberUpdateInSchema,
    RoomSchema,
)
from core.apps.common.authentication.bearer import jwt_bearer_admin
from core.apps.common.exceptions import ServiceException
from core.apps.common.filters import SearchFilter as SearchFilterEntity
from core.apps.schedule.services.room import BaseRoomService
from core.project.containers.containers import get_container


router = Router(tags=["Rooms"])


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
    service: BaseRoomService = container.resolve(BaseRoomService)
    try:
        room_list = service.get_room_list(
            filters=SearchFilterEntity(search=filters.search),
            pagination=pagination_in,
        )
        room_count = service.get_room_count(filters=filters)

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
    operation_id="get_or_create_room",
    auth=jwt_bearer_admin,
)
def get_or_create_room(request: HttpRequest, schema: RoomNumberInSchema) -> ApiResponse[RoomSchema]:
    container = get_container()
    service: BaseRoomService = container.resolve(BaseRoomService)
    try:
        room = service.get_or_create(number=schema.number)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=RoomSchema.from_entity(entity=room),
    )


@router.patch(
    "change_number",
    response=ApiResponse[RoomSchema],
    operation_id="update_room_number",
    auth=jwt_bearer_admin,
)
def update_room_number(
    request: HttpRequest,
    schema: RoomNumberUpdateInSchema,
) -> ApiResponse[RoomSchema]:
    container = get_container()
    service: BaseRoomService = container.resolve(BaseRoomService)
    try:
        room = service.update_room_number(room_uuid=schema.room_uuid, new_number=schema.new_room_number)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=RoomSchema.from_entity(entity=room),
    )


@router.patch(
    "change_description",
    response=ApiResponse[RoomSchema],
    operation_id="update_room_description",
    auth=jwt_bearer_admin,
)
def update_room_description(
    request: HttpRequest,
    schema: RoomDescriptionUpdateInSchema,
) -> ApiResponse[RoomSchema]:
    container = get_container()
    service: BaseRoomService = container.resolve(BaseRoomService)
    try:
        room = service.update_room_description(room_uuid=schema.room_uuid, description=schema.description)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=RoomSchema.from_entity(entity=room),
    )


@router.delete(
    "{room_uuid}", response=ApiResponse[StatusResponse],
    operation_id="delete_room_by_uuid",
    auth=jwt_bearer_admin,
)
def delete_room(request: HttpRequest, room_uuid: str) -> ApiResponse[StatusResponse]:
    container = get_container()
    service: BaseRoomService = container.resolve(BaseRoomService)
    try:
        service.delete_room_by_uuid(room_uuid=room_uuid)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=StatusResponse(
            status="Room deleted successfully",
        ),
    )
