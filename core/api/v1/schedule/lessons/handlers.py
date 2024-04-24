from django.http import HttpRequest
from ninja import (
    Query,
    Router,
)
from ninja.errors import HttpError

from core.api.schemas import ApiResponse
from core.api.v1.schedule.lessons.schema import (
    CreateLessonInSchema,
    LessonInSchema,
    LessonOutSchema,
)
from core.apps.common.authentication.bearer import jwt_bearer
from core.apps.common.exceptions import ServiceException
from core.apps.schedule.use_cases.lessons.create import CreateLessonUseCase
from core.project.containers import get_container


router = Router(tags=["Lessons"])


@router.post("", response=ApiResponse[LessonOutSchema], operation_id="create_lesson", auth=jwt_bearer)
def create_lesson(
    request: HttpRequest,
    schema: Query[CreateLessonInSchema],
    lesson_schema: Query[LessonInSchema],
) -> ApiResponse[LessonOutSchema]:
    container = get_container()
    use_case: CreateLessonUseCase = container.resolve(CreateLessonUseCase)

    try:
        lesson = use_case.execute(
            lesson=lesson_schema.to_entity(),
            subject_id=schema.subject_id,
            teacher_id=schema.teacher_id,
            room_id=schema.room_id,
            timeslot_id=schema.timeslot_id,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(data=LessonOutSchema.from_entity(lesson))
