from django.http import HttpResponse
from django.http import HttpRequest
from ninja import Router, Query
from ninja.errors import HttpError

from core.api.filters import PaginationIn, SearchFilter, PaginationOut
from core.api.schemas import ApiResponse, ListPaginatedResponse, StatusResponse
from core.api.v1.schedule.rooms.schemas import (RoomSchema, RoomNumberInSchema, RoomDescriptionUpdateInSchema,
                                                RoomNumberUpdateInSchema)
from core.apps.common.authentication import auth_bearer
from core.apps.common.exceptions import ServiceException
from core.apps.common.filters import SearchFilter as SearchFilterEntity
from core.api.v1.schedule.rooms.containers import room_service

router = Router(tags=["Rooms"])


@router.get("",
            response=ApiResponse[ListPaginatedResponse[RoomSchema]],
            operation_id="get_room_list")
def get_room_list(request: HttpRequest,
                  filters: Query[SearchFilter],
                  pagination_in: Query[PaginationIn]) -> ApiResponse[ListPaginatedResponse[RoomSchema]]:
    try:
        room_list = room_service.get_room_list(filters=SearchFilterEntity(search=filters.search),
                                               pagination=pagination_in)
        room_count = room_service.get_room_count(filters=filters)

        items = [RoomSchema.from_entity(obj) for obj in room_list]

        pagination_out = PaginationOut(
            offset=pagination_in.offset,
            limit=pagination_in.limit,
            total=room_count,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message
        )

    return ApiResponse(data=ListPaginatedResponse(
        items=items,
        pagination=pagination_out
    ))


@router.post("",
             response=ApiResponse[RoomSchema],
             operation_id="get_or_create_room",
             auth=auth_bearer)
def get_or_create_room(request: HttpRequest, schema: RoomNumberInSchema) -> ApiResponse[RoomSchema]:
    try:
        room = room_service.get_or_create(number=schema.number)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message
        )

    return ApiResponse(data=RoomSchema(
        number=room.number,
        description=room.description
    ))


@router.patch("number",
              response=ApiResponse[RoomSchema],
              operation_id="update_room_number",
              auth=auth_bearer)
def update_room_number(request: HttpRequest,
                       schema: RoomNumberUpdateInSchema) -> ApiResponse[RoomSchema]:
    try:
        room = room_service.update_room_number(number=schema.number, new_number=schema.new_number)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message
        )

    return ApiResponse(data=RoomSchema(
        number=room.number,
        description=room.description
    ))


@router.patch("description",
              response=ApiResponse[RoomSchema],
              operation_id="update_room_description",
              auth=auth_bearer)
def update_room_description(request: HttpRequest,
                            schema: RoomDescriptionUpdateInSchema) -> ApiResponse[RoomSchema]:
    try:
        room = room_service.update_room_description(number=schema.number, description=schema.description)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message
        )

    return ApiResponse(data=RoomSchema(
        number=room.number,
        description=room.description
    ))


@router.delete("", response=ApiResponse[StatusResponse],
               operation_id="delete_room_by_number",
               auth=auth_bearer)
def delete_room(request: HttpRequest, schema: RoomNumberInSchema) -> ApiResponse[StatusResponse]:
    try:
        room_service.delete_room_by_number(number=schema.number)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message
        )

    return ApiResponse(data=StatusResponse(
        status=f"Room deleted successfully"
    ))
