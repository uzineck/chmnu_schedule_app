from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError

from core.api.schemas import ApiResponse
from core.api.v1.time.schemas import TimeInfoOutSchema
from core.apps.common.exceptions import ServiceException
from core.apps.common.time.use_case import GetCurrentTimeInfo
from core.project.containers.containers import get_container


router = Router(tags=["Time"])


@router.get(
    "current",
    response=ApiResponse[TimeInfoOutSchema],
    operation_id="get_current_time_info",
)
def get_current_time_info(request: HttpRequest) -> ApiResponse[TimeInfoOutSchema]:
    container = get_container()
    use_case: GetCurrentTimeInfo = container.resolve(GetCurrentTimeInfo)
    try:
        time_info = use_case.execute()
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )
    return ApiResponse(
        data=TimeInfoOutSchema.from_entity(entity=time_info),
    )
