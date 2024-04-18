from django.http import HttpResponse
from django.http import HttpRequest
from ninja import Router, Query
from ninja.errors import HttpError

from core.api.schemas import ApiResponse
from core.api.v1.schedule.timeslots.schemas import TimeslotSchema
from core.apps.common.authentication import auth_bearer
from core.apps.common.exceptions import ServiceException
from core.api.v1.schedule.timeslots.containers import timeslot_service

router = Router(tags=["Timeslots"])


@router.post("", response=ApiResponse[TimeslotSchema], operation_id="get_or_create_timeslot", auth=auth_bearer)
def get_or_create_timeslot(request:HttpRequest, schema: TimeslotSchema) -> ApiResponse[TimeslotSchema]:
    try:
        timeslot = timeslot_service.get_or_create(day=schema.day, ord_number=schema.ord_number, is_even=schema.is_even)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message
        )
    return ApiResponse(data=TimeslotSchema(
        day=timeslot.day,
        ord_number=timeslot.ord_number,
        is_even=timeslot.is_even
    ))
