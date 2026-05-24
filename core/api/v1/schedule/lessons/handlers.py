from django.http import HttpRequest
from ninja import Router

from core.api.schemas import (
    ApiErrorResponse,
    ApiResponse,
)
from core.api.v1.schedule.lessons.schema_for_groups import (
    LessonForGroupOutSchema,
    UpdatedLessonOutSchema,
)
from core.api.v1.schedule.lessons.schemas import (
    CreateLessonInSchema,
    LessonInSchema,
)
from core.apps.common.authentication.ninja_auth import jwt_auth_schedule_or_headman
from core.apps.schedule.use_cases.lesson.get_or_create import GetOrCreateLessonUseCase
from core.apps.schedule.use_cases.lesson.update import UpdateLessonUseCase
from core.project.containers.containers import get_container


router = Router(tags=["Lessons"])


@router.post(
    "",
    response={
        201: ApiResponse[LessonForGroupOutSchema],
        400: ApiErrorResponse,
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
    },
    operation_id="get_or_create_lesson",
    auth=jwt_auth_schedule_or_headman,
    summary="Get-or-create a lesson definition",
    description=(
        "Returns the existing lesson matching the supplied (subject, teacher, room, timeslot, "
        "type) combination, or creates a fresh one if no match exists. The request body wraps "
        "two nested payloads:\n\n"
        "- `schema` — references to the related catalog entities (`subject_uuid`, `teacher_uuid`, "
        "`room_uuid`).\n"
        "- `lesson_schema` — the lesson's own attributes (`type` and `timeslot`).\n\n"
        "The response does not include `subgroups`; that field is only populated when the lesson "
        "is fetched in the context of a specific group. Requires ADMIN, SCHEDULE_MANAGER, or "
        "HEADMAN role."
    ),
)
def get_or_create_lesson(
    request: HttpRequest,
    schema: CreateLessonInSchema,
    lesson_schema: LessonInSchema,
) -> tuple[int, ApiResponse[LessonForGroupOutSchema]]:
    container = get_container()
    use_case: GetOrCreateLessonUseCase = container.resolve(GetOrCreateLessonUseCase)

    lesson = use_case.execute(
        lesson=lesson_schema.to_entity(),
        subject_uuid=schema.subject_uuid,
        teacher_uuid=schema.teacher_uuid,
        room_uuid=schema.room_uuid,
    )

    return 201, ApiResponse(data=LessonForGroupOutSchema.from_entity(lesson))


@router.patch(
    "{lesson_uuid}/update",
    response={
        200: ApiResponse[UpdatedLessonOutSchema],
        400: ApiErrorResponse,
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
        409: ApiErrorResponse,
    },
    operation_id="update_lesson",
    auth=jwt_auth_schedule_or_headman,
    summary="Update a lesson definition",
    description=(
        "Replaces the lesson identified by `lesson_uuid` with a new (subject, teacher, room, "
        "timeslot, type) combination. The response returns both the `updated_lesson` and the "
        "`old_lesson` snapshot so the client can refresh local caches without an extra fetch. "
        "Requires ADMIN, SCHEDULE_MANAGER, or HEADMAN role."
    ),
)
def update_lesson(
    request: HttpRequest,
    lesson_uuid: str,
    schema: CreateLessonInSchema,
    lesson_schema: LessonInSchema,
) -> ApiResponse[UpdatedLessonOutSchema]:
    container = get_container()
    use_case: UpdateLessonUseCase = container.resolve(UpdateLessonUseCase)

    lesson, old_lesson = use_case.execute(
        lesson_uuid=lesson_uuid,
        lesson=lesson_schema.to_entity(),
        subject_uuid=schema.subject_uuid,
        teacher_uuid=schema.teacher_uuid,
        room_uuid=schema.room_uuid,
    )

    return ApiResponse(data=UpdatedLessonOutSchema.from_entity(updated_lesson=lesson, old_lesson=old_lesson))
