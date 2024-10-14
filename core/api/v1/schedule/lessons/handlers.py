from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError

from core.api.schemas import ApiResponse
from core.api.v1.schedule.lessons.schema_for_groups import (
    CreateLessonInSchema,
    LessonForGroupOutSchema,
    LessonInSchema,
)
from core.apps.common.authentication.bearer import jwt_bearer
from core.apps.common.exceptions import ServiceException
from core.apps.schedule.use_cases.lesson.create import CreateLessonUseCase
from core.project.containers.containers import get_container


router = Router(tags=["Lessons"])


@router.post("", response=ApiResponse[LessonForGroupOutSchema], operation_id="create_lesson", auth=jwt_bearer)
def create_lesson(
    request: HttpRequest,
    schema: CreateLessonInSchema,
    lesson_schema: LessonInSchema,
) -> ApiResponse[LessonForGroupOutSchema]:
    container = get_container()
    use_case: CreateLessonUseCase = container.resolve(CreateLessonUseCase)

    try:
        lesson = use_case.execute(
            lesson=lesson_schema.to_entity(),
            subject_uuid=schema.subject_uuid,
            teacher_uuid=schema.teacher_uuid,
            room_uuid=schema.room_uuid,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(data=LessonForGroupOutSchema.from_entity(lesson))
