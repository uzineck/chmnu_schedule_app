from django.http import HttpRequest
from ninja import (
    Query,
    Router,
)
from ninja.errors import HttpError

from core.api.filters import (
    PaginationIn,
    PaginationOut,
)
from core.api.schemas import (
    ApiResponse,
    ListPaginatedResponse,
)
from core.api.v1.schedule.lessons.schema_for_teachers import (
    LessonForTeacherOutSchema,
    TeacherLessonsOutSchema,
)
from core.api.v1.schedule.teachers.filters import TeacherFilter
from core.api.v1.schedule.teachers.schemas import (
    TeacherInSchema,
    TeacherSchema,
)
from core.apps.common.authentication.bearer import jwt_bearer_admin
from core.apps.common.exceptions import ServiceException
from core.apps.schedule.filters.teacher import TeacherFilter as TeacherFilterEntity
from core.apps.schedule.services.teacher import BaseTeacherService
from core.apps.schedule.use_cases.teacher.get_lessons_for_teacher import GetLessonsForTeacherUseCase
from core.project.containers.containers import get_container


router = Router(tags=["Teachers"])


@router.get(
    "",
    response=ApiResponse[ListPaginatedResponse[TeacherSchema]],
    operation_id="get_teacher_list",
)
def get_teacher_list(
        request: HttpRequest,
        filters: Query[TeacherFilter],
        pagination_in: Query[PaginationIn],
) -> ApiResponse[ListPaginatedResponse[TeacherSchema]]:
    container = get_container()
    service: BaseTeacherService = container.resolve(BaseTeacherService)
    try:
        teacher_list = service.get_teacher_list(
            filters=TeacherFilterEntity(
                name=filters.name,
                rank=filters.rank,
            ),
            pagination=pagination_in,
        )
        teacher_count = service.get_teacher_count(filters=filters)

        items = [TeacherSchema.from_entity(obj) for obj in teacher_list]

        pagination_out = PaginationOut(
            offset=pagination_in.offset,
            limit=pagination_in.limit,
            total=teacher_count,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=ListPaginatedResponse(
            items=items,
            pagination=pagination_out,
        ),
    )


@router.get(
    "{teacher_uuid}/lessons",
    response=ApiResponse[TeacherLessonsOutSchema],
    operation_id="get_lessons_for_teacher",
)
def get_lessons_for_teacher(request: HttpRequest, teacher_uuid: str) -> ApiResponse[TeacherLessonsOutSchema]:
    container = get_container()
    use_case: GetLessonsForTeacherUseCase = container.resolve(GetLessonsForTeacherUseCase)
    try:
        teacher, lessons, groups = use_case.execute(
            teacher_uuid=teacher_uuid,
        )

        items = []
        for lesson in lessons:
            group_entities = groups.get(lesson.id)
            lesson_schema = LessonForTeacherOutSchema.from_entity(lesson, group_entities)
            items.append(lesson_schema)

    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=TeacherLessonsOutSchema(
            teacher=teacher,
            lessons=items,
        ),
    )


@router.post(
    "",
    response=ApiResponse[TeacherSchema],
    operation_id="get_or_create_teacher",
    auth=jwt_bearer_admin,
)
def get_or_create_teacher(request: HttpRequest, schema: TeacherInSchema) -> ApiResponse[TeacherSchema]:
    container = get_container()
    service: BaseTeacherService = container.resolve(BaseTeacherService)
    try:
        teacher = service.get_or_create(
            first_name=schema.first_name,
            last_name=schema.last_name,
            middle_name=schema.middle_name,
            rank=schema.rank,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=TeacherSchema.from_entity(entity=teacher),
    )


@router.patch(
    "{teacher_uuid}/update",
    response=ApiResponse[TeacherSchema],
    operation_id="update_teacher",
    auth=jwt_bearer_admin,
)
def update_teacher(
        request: HttpRequest,
        teacher_uuid: str,
        schema: TeacherInSchema,
) -> ApiResponse[TeacherSchema]:
    container = get_container()
    service = container.resolve(BaseTeacherService)
    try:
        teacher = service.update_teacher_by_uuid(
            teacher_uuid=teacher_uuid,
            first_name=schema.first_name,
            last_name=schema.last_name,
            middle_name=schema.middle_name,
            rank=schema.rank,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=TeacherSchema.from_entity(entity=teacher),
    )
