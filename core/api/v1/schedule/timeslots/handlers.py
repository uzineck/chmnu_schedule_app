from django.http import HttpRequest
from ninja import (
    Form,
    Router,
)

from core.api.schemas import (
    ApiErrorResponse,
    ApiResponse,
)
from core.api.v1.schedule.timeslots.schemas import (
    CreateTimeslotSchema,
    TimeslotSchema,
)
from core.apps.common.authentication.ninja_auth import jwt_auth_admin
from core.apps.schedule.use_cases.timeslot.get_or_create import CreateTimeslotUseCase
from core.project.containers.containers import get_container


router = Router(tags=["Timeslots"])


@router.post(
    "",
    response={
        201: ApiResponse[TimeslotSchema],
        400: ApiErrorResponse,
        401: ApiErrorResponse,
        403: ApiErrorResponse,
    },
    operation_id="get_or_create_timeslot",
    auth=jwt_auth_admin,
    summary="Get-or-create a timeslot",
    description=(
        "Returns the existing timeslot for the (day, ord_number, is_even) tuple or creates a new "
        "one if none exists. The body is `application/x-www-form-urlencoded`. Requires ADMIN role."
    ),
)
def get_or_create_timeslot(
        request: HttpRequest,
        schema: Form[CreateTimeslotSchema],
) -> tuple[int, ApiResponse[TimeslotSchema]]:
    container = get_container()
    use_case: CreateTimeslotUseCase = container.resolve(CreateTimeslotUseCase)
    timeslot = use_case.execute(day=schema.day, ord_number=schema.ord_number, is_even=schema.is_even)
    return 201, ApiResponse(
        data=TimeslotSchema.from_entity(entity=timeslot),
    )
