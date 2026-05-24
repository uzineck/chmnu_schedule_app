from django.http import HttpRequest
from ninja import (
    Query,
    Router,
)

from core.api.filters import (
    PaginationIn,
    PaginationOut,
)
from core.api.schemas import (
    ApiErrorResponse,
    ApiResponse,
    ListPaginatedResponse,
    StatusResponse,
)
from core.api.v1.schedule.lessons.schema_for_teachers import TeacherLessonsOutSchema
from core.api.v1.schedule.teachers.filters import (
    TeacherFilter,
    TeacherLessonFilter,
)
from core.api.v1.schedule.teachers.schemas import (
    TeacherInSchema,
    TeacherNameInSchema,
    TeacherRankInSchema,
    TeacherSchema,
)
from core.apps.common.authentication.ninja_auth import (
    jwt_auth,
    jwt_auth_teacher_manager,
)
from core.apps.schedule.filters.group import LessonFilter
from core.apps.schedule.filters.teacher import TeacherFilter as TeacherFilterEntity
from core.apps.schedule.use_cases.teacher.create import CreateTeacherUseCase
from core.apps.schedule.use_cases.teacher.delete import DeleteTeacherUseCase
from core.apps.schedule.use_cases.teacher.get_all import GetAllTeachersUseCase
from core.apps.schedule.use_cases.teacher.get_list import GetTeacherListUseCase
from core.apps.schedule.use_cases.teacher.get_teacher_lessons import GetLessonsForTeacherUseCase
from core.apps.schedule.use_cases.teacher.update_name import UpdateTeacherNameUseCase
from core.apps.schedule.use_cases.teacher.update_rank import UpdateTeacherRankUseCase
from core.project.containers.containers import get_container


router = Router(tags=["Teachers"])


@router.get(
    'all',
    response=ApiResponse[list[TeacherSchema]],
    operation_id='get_all_teachers',
    summary="List every active teacher (public)",
    description=(
        "Returns the full collection of active teachers — no pagination, no filtering. Intended "
        "for dropdowns and public lookups. Use `get_teacher_list` for paginated / filterable "
        "access."
    ),
)
def get_all_teachers(request: HttpRequest) -> ApiResponse[list[TeacherSchema]]:
    container = get_container()
    use_case: GetAllTeachersUseCase = container.resolve(GetAllTeachersUseCase)
    items = [TeacherSchema.from_entity(obj) for obj in use_case.execute()]
    return ApiResponse(
        data=items,
    )


@router.get(
    "",
    response={
        200: ApiResponse[ListPaginatedResponse[TeacherSchema]],
        401: ApiErrorResponse,
    },
    operation_id="get_teacher_list",
    auth=jwt_auth,
    summary="Filter and paginate teachers",
    description=(
        "Returns a paginated list of active teachers. `name` is a single search term matched "
        "case-insensitively against first, last, and middle names — whitespace splits it into "
        "tokens, and every token must appear in at least one of those columns (so `Smith John` "
        "finds `John Smith`). `rank` is an optional case-insensitive contains match."
    ),
)
def get_teacher_list(
        request: HttpRequest,
        filters: Query[TeacherFilter],
        pagination_in: Query[PaginationIn],
) -> ApiResponse[ListPaginatedResponse[TeacherSchema]]:
    container = get_container()
    use_case: GetTeacherListUseCase = container.resolve(GetTeacherListUseCase)
    item_list, item_count = use_case.execute(
        filters=TeacherFilterEntity(
            name=filters.name,
            rank=filters.rank,
        ),
        pagination_in=pagination_in,
    )
    pagination_out = PaginationOut(
        offset=pagination_in.offset,
        limit=pagination_in.limit,
        total=item_count,
    )

    return ApiResponse(
        data=ListPaginatedResponse(
            items=[TeacherSchema.from_entity(obj) for obj in item_list],
            pagination=pagination_out,
        ),
    )


@router.get(
    "{teacher_uuid}/lessons",
    response={
        200: ApiResponse[TeacherLessonsOutSchema],
        404: ApiErrorResponse,
    },
    operation_id="get_lessons_for_teacher",
    summary="Get a teacher's schedule (public)",
    description=(
        "Returns every lesson the teacher leads for the requested week parity, along with the "
        "groups (and subgroups) each lesson is attached to. Public — no authentication required."
    ),
)
def get_lessons_for_teacher(
        request: HttpRequest,
        teacher_uuid: str,
        filters: Query[TeacherLessonFilter],
) -> ApiResponse[TeacherLessonsOutSchema]:
    container = get_container()
    use_case: GetLessonsForTeacherUseCase = container.resolve(GetLessonsForTeacherUseCase)
    teacher, views = use_case.execute(
        teacher_uuid=teacher_uuid,
        filters=LessonFilter(is_even=filters.is_even),
    )

    return ApiResponse(
        data=TeacherLessonsOutSchema.from_views(teacher=teacher, views=views),
    )


@router.post(
    "",
    response={
        201: ApiResponse[TeacherSchema],
        400: ApiErrorResponse,
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        409: ApiErrorResponse,
    },
    operation_id="create_teacher",
    auth=jwt_auth_teacher_manager,
    summary="Create a teacher",
    description=(
        "Registers a new teacher with name and academic rank. Returns 409 if a teacher with the "
        "same full name already exists. Requires ADMIN or TEACHER_MANAGER role."
    ),
)
def create_teacher(
        request: HttpRequest,
        schema: TeacherInSchema,
) -> tuple[int, ApiResponse[TeacherSchema]]:
    container = get_container()
    use_case: CreateTeacherUseCase = container.resolve(CreateTeacherUseCase)
    teacher = use_case.execute(
        first_name=schema.first_name,
        last_name=schema.last_name,
        middle_name=schema.middle_name,
        rank=schema.rank,
    )

    return 201, ApiResponse(
        data=TeacherSchema.from_entity(entity=teacher),
    )


@router.patch(
    "{teacher_uuid}/update_name",
    response={
        200: ApiResponse[TeacherSchema],
        400: ApiErrorResponse,
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
        409: ApiErrorResponse,
    },
    operation_id="update_teacher_name",
    auth=jwt_auth_teacher_manager,
    summary="Rename a teacher",
    description="Updates the teacher's first/last/middle name. Rank is left untouched.",
)
def update_teacher_name(
        request: HttpRequest,
        teacher_uuid: str,
        schema: TeacherNameInSchema,
) -> ApiResponse[TeacherSchema]:
    container = get_container()
    use_case: UpdateTeacherNameUseCase = container.resolve(UpdateTeacherNameUseCase)
    teacher = use_case.execute(
        teacher_uuid=teacher_uuid,
        first_name=schema.first_name,
        last_name=schema.last_name,
        middle_name=schema.middle_name,
    )
    return ApiResponse(
        data=TeacherSchema.from_entity(entity=teacher),
    )


@router.patch(
    "{teacher_uuid}/update_rank",
    response={
        200: ApiResponse[TeacherSchema],
        400: ApiErrorResponse,
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
    },
    operation_id="update_teacher_rank",
    auth=jwt_auth_teacher_manager,
    summary="Change a teacher's rank",
    description="Updates the teacher's academic rank (e.g. Assistant, Docent, Professor).",
)
def update_teacher_rank(
        request: HttpRequest,
        teacher_uuid: str,
        schema: TeacherRankInSchema,
) -> ApiResponse[TeacherSchema]:
    container = get_container()
    use_case: UpdateTeacherRankUseCase = container.resolve(UpdateTeacherRankUseCase)
    teacher = use_case.execute(
        teacher_uuid=teacher_uuid,
        rank=schema.rank,
    )
    return ApiResponse(
        data=TeacherSchema.from_entity(entity=teacher),
    )


@router.delete(
    "{teacher_uuid}",
    response={
        200: ApiResponse[StatusResponse],
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
        409: ApiErrorResponse,
    },
    operation_id="delete_teacher",
    auth=jwt_auth_teacher_manager,
    summary="Soft-delete a teacher",
    description="Marks the teacher inactive. Returns 409 if the teacher is still assigned to any active lesson.",
)
def delete_teacher(
    request: HttpRequest,
    teacher_uuid: str,
) -> ApiResponse[StatusResponse]:
    container = get_container()
    use_case: DeleteTeacherUseCase = container.resolve(DeleteTeacherUseCase)
    use_case.execute(teacher_uuid=teacher_uuid)

    return ApiResponse(
        data=StatusResponse(status="Teacher deleted successfully"),
    )
