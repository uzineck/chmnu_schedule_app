from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError

from core.api.schemas import ApiResponse
from core.api.v1.schedule.lessons.schema_for_groups import (
    LessonForGroupOutSchema,
    UpdatedLessonOutSchema,
)
from core.api.v1.schedule.lessons.schemas import (
    CreateLessonInSchema,
    LessonInSchema,
)
from core.apps.common.authentication.bearer import jwt_bearer
from core.apps.common.exceptions import ServiceException
from core.apps.schedule.use_cases.lesson.get_or_create import GetOrCreateLessonUseCase
from core.apps.schedule.use_cases.lesson.update import UpdateLessonUseCase
from core.project.containers.containers import get_container


router = Router(tags=["Lessons"])


@router.post(
    "",
    response={201: ApiResponse[LessonForGroupOutSchema]},
    operation_id="get_or_create_lesson",
    auth=jwt_bearer,
)
def get_or_create_lesson(
    request: HttpRequest,
    schema: CreateLessonInSchema,
    lesson_schema: LessonInSchema,
) -> ApiResponse[LessonForGroupOutSchema]:
    container = get_container()
    use_case: GetOrCreateLessonUseCase = container.resolve(GetOrCreateLessonUseCase)

    try:
        lesson = use_case.execute(
            lesson=lesson_schema.to_entity(),
            subject_uuid=schema.subject_uuid,
            teacher_uuid=schema.teacher_uuid,
            room_uuid=schema.room_uuid,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )

    return ApiResponse(data=LessonForGroupOutSchema.from_entity(lesson))


@router.patch(
    "{lesson_uuid}/update",
    response=ApiResponse[UpdatedLessonOutSchema],
    operation_id="update_lesson",
    auth=jwt_bearer,
)
def update_lesson(
    request: HttpRequest,
    lesson_uuid: str,
    schema: CreateLessonInSchema,
    lesson_schema: LessonInSchema,
) -> ApiResponse[UpdatedLessonOutSchema]:
    container = get_container()
    use_case: UpdateLessonUseCase = container.resolve(UpdateLessonUseCase)

    try:
        lesson, old_lesson = use_case.execute(
            lesson_uuid=lesson_uuid,
            lesson=lesson_schema.to_entity(),
            subject_uuid=schema.subject_uuid,
            teacher_uuid=schema.teacher_uuid,
            room_uuid=schema.room_uuid,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )

    return ApiResponse(data=UpdatedLessonOutSchema.from_entity(updated_lesson=lesson, old_lesson=old_lesson))
