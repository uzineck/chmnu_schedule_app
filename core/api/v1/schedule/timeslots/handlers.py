from django.http import HttpRequest
from ninja import (
    Form,
    Query,
    Router,
)
from ninja.errors import HttpError

from core.api.schemas import ApiResponse
from core.api.v1.schedule.timeslots.schemas import (
    CreateTimeslotSchema,
    TimeslotInSchema,
    TimeslotSchema,
)
from core.apps.common.authentication.bearer import jwt_bearer
from core.apps.common.exceptions import ServiceException
from core.apps.schedule.services.timeslot import BaseTimeslotService
from core.project.containers.containers import get_container


router = Router(tags=["Timeslots"])


@router.get(
    "",
    response=ApiResponse[TimeslotSchema],
    operation_id="get_timeslot_by_id",
    auth=jwt_bearer,
    deprecated=True,
)
def get_timeslot_by_id(request: HttpRequest, schema: Query[TimeslotInSchema]) -> ApiResponse[TimeslotSchema]:
    container = get_container()
    service = container.resolve(BaseTimeslotService)
    try:
        timeslot = service.get_timeslot_by_id(timeslot_id=schema.timeslot_id)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )
    return ApiResponse(
        data=TimeslotSchema.from_entity(entity=timeslot),
    )


@router.post("", response=ApiResponse[TimeslotSchema], operation_id="get_or_create_timeslot", auth=jwt_bearer)
def get_or_create_timeslot(request: HttpRequest, schema: Form[CreateTimeslotSchema]) -> ApiResponse[TimeslotSchema]:
    container = get_container()
    service = container.resolve(BaseTimeslotService)
    try:
        timeslot = service.create(day=schema.day, ord_number=schema.ord_number, is_even=schema.is_even)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )
    return ApiResponse(
        data=TimeslotSchema.from_entity(entity=timeslot),
    )


