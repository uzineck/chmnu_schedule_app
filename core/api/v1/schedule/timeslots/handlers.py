from django.http import HttpRequest
from ninja import (
    Form,
    Router,
)
from ninja.errors import HttpError

from core.api.schemas import ApiResponse
from core.api.v1.schedule.timeslots.schemas import (
    CreateTimeslotSchema,
    TimeslotSchema,
)
from core.apps.common.authentication.bearer import jwt_bearer_admin
from core.apps.common.exceptions import ServiceException
from core.apps.schedule.use_cases.timeslot.get_or_create import CreateTimeslotUseCase
from core.project.containers.containers import get_container


router = Router(tags=["Timeslots"])


@router.post(
    "",
    response=ApiResponse[TimeslotSchema],
    operation_id="get_or_create_timeslot",
    auth=jwt_bearer_admin,
)
def get_or_create_timeslot(request: HttpRequest, schema: Form[CreateTimeslotSchema]) -> ApiResponse[TimeslotSchema]:
    container = get_container()
    use_case: CreateTimeslotUseCase = container.resolve(CreateTimeslotUseCase)
    try:
        timeslot = use_case.execute(day=schema.day, ord_number=schema.ord_number, is_even=schema.is_even)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )
    return ApiResponse(
        data=TimeslotSchema.from_entity(entity=timeslot),
    )
