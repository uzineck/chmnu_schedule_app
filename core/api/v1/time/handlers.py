from django.http import HttpRequest
from ninja import Router

from core.api.schemas import ApiResponse
from core.api.v1.time.schemas import TimeInfoOutSchema
from core.apps.common.time.use_case import GetCurrentTimeInfoUseCase
from core.project.containers.containers import get_container


router = Router(tags=["Time"])


@router.get(
    "current",
    response=ApiResponse[TimeInfoOutSchema],
    operation_id="get_current_time_info",
    summary="Get the current academic week context",
    description=(
        "Returns the server's view of the current academic week: whether it is even or odd "
        "relative to the semester start, the current weekday index (1=Monday … 7=Sunday), and "
        "the ordinal number of the lesson currently in session (0 if outside teaching hours). "
        "Used by clients to highlight 'today / now' in the schedule. Public — no authentication "
        "required."
    ),
)
def get_current_time_info(request: HttpRequest) -> ApiResponse[TimeInfoOutSchema]:
    container = get_container()
    use_case: GetCurrentTimeInfoUseCase = container.resolve(GetCurrentTimeInfoUseCase)
    time_info = use_case.execute()
    return ApiResponse(
        data=TimeInfoOutSchema.from_entity(entity=time_info),
    )
