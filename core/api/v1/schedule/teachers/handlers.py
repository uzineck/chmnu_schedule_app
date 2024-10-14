from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError

from core.api.filters import (
    PaginationIn,
    PaginationOut,
)
from core.api.schemas import (
    ApiResponse,
    ListPaginatedResponse,
    StatusResponse,
)
from core.api.v1.schedule.lessons.schema_for_teachers import (
    LessonForTeacherOutSchema,
    TeacherLessonsOutSchema,
)
from core.api.v1.schedule.teachers.filters import TeacherFilter
from core.api.v1.schedule.teachers.schemas import (
    TeacherInSchema,
    TeacherNameInSchema,
    TeacherRankInSchema,
    TeacherSchema,
)
from core.apps.common.authentication.bearer import jwt_bearer_admin
from core.apps.common.exceptions import ServiceException
from core.apps.schedule.filters.teacher import TeacherFilter as TeacherFilterEntity
from core.apps.schedule.use_cases.teacher.create import CreateTeacherUseCase
from core.apps.schedule.use_cases.teacher.deactivate import DeactivateTeacherUseCase
from core.apps.schedule.use_cases.teacher.get_all import GetAllTeachersUseCase
from core.apps.schedule.use_cases.teacher.get_list import GetTeacherListUseCase
from core.apps.schedule.use_cases.teacher.get_teacher_lessons import GetLessonsForTeacherUseCase
from core.apps.schedule.use_cases.teacher.update_name import UpdateTeacherNameUseCase
from core.apps.schedule.use_cases.teacher.update_rank import UpdateTeacherRankUseCase
from core.project.containers.containers import get_container


router = Router(tags=["Teachers"])


@router.get(
    'all',
    response=ApiResponse,
    operation_id='get_all_teachers',

)
def get_all_teachers(request: HttpRequest) -> ApiResponse:
    container = get_container()
    use_case: GetAllTeachersUseCase = container.resolve(GetAllTeachersUseCase)
    teachers = use_case.execute()
    items = [TeacherSchema.from_entity(obj) for obj in teachers]

    return ApiResponse(
        data=items,
    )


@router.get(
    "",
    response=ApiResponse[ListPaginatedResponse[TeacherSchema]],
    operation_id="get_teacher_list",
)
def get_teacher_list(
        request: HttpRequest,
        filters: TeacherFilter,
        pagination_in: PaginationIn,
) -> ApiResponse[ListPaginatedResponse[TeacherSchema]]:
    container = get_container()
    use_case: GetTeacherListUseCase = container.resolve(GetTeacherListUseCase)
    try:
        teacher_list, teacher_count = use_case.execute(
            filters=TeacherFilterEntity(
                name=filters.name,
                rank=filters.rank,
            ),
            pagination=pagination_in,
        )
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
    operation_id="create_teacher",
    auth=jwt_bearer_admin,
)
def create_teacher(request: HttpRequest, schema: TeacherInSchema) -> ApiResponse[TeacherSchema]:
    container = get_container()
    use_case: CreateTeacherUseCase = container.resolve(CreateTeacherUseCase)
    try:
        teacher = use_case.execute(
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
    "{teacher_uuid}/update_name",
    response=ApiResponse[TeacherSchema],
    operation_id="update_teacher_name",
    auth=jwt_bearer_admin,
)
def update_teacher_name(
        request: HttpRequest,
        teacher_uuid: str,
        schema: TeacherNameInSchema,
) -> ApiResponse[TeacherSchema]:
    container = get_container()
    use_case: UpdateTeacherNameUseCase = container.resolve(UpdateTeacherNameUseCase)
    try:
        teacher = use_case.execute(
            teacher_uuid=teacher_uuid,
            first_name=schema.first_name,
            last_name=schema.last_name,
            middle_name=schema.middle_name,
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
    "{teacher_uuid}/update_rank",
    response=ApiResponse[TeacherSchema],
    operation_id="update_teacher_rank",
    auth=jwt_bearer_admin,
)
def update_teacher_rank(
        request: HttpRequest,
        teacher_uuid: str,
        schema: TeacherRankInSchema,
) -> ApiResponse[TeacherSchema]:
    container = get_container()
    use_case: UpdateTeacherRankUseCase = container.resolve(UpdateTeacherRankUseCase)
    try:
        teacher = use_case.execute(
            teacher_uuid=teacher_uuid,
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


@router.delete(
    "{teacher_uuid}",
    response=ApiResponse[StatusResponse],
    operation_id="delete_teacher",
    auth=jwt_bearer_admin,
)
def delete_teacher(
        request: HttpRequest,
        teacher_uuid: str,
) -> ApiResponse[StatusResponse]:
    container = get_container()
    use_case: DeactivateTeacherUseCase = container.resolve(DeactivateTeacherUseCase)
    try:
        use_case.execute(
            teacher_uuid=teacher_uuid,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )
    return ApiResponse(
        data=StatusResponse(status="Teacher deleted successfully"),
    )
