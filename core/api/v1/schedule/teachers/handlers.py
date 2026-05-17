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
    response=ApiResponse[ListPaginatedResponse[TeacherSchema]],
    operation_id="get_teacher_list",
    auth=jwt_auth,
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
            first_name=filters.first_name,
            last_name=filters.last_name,
            middle_name=filters.middle_name,
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
    response=ApiResponse[TeacherLessonsOutSchema],
    operation_id="get_lessons_for_teacher",
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
    response={201: ApiResponse[TeacherSchema]},
    operation_id="create_teacher",
    auth=jwt_auth_teacher_manager,
)
def create_teacher(request: HttpRequest, schema: TeacherInSchema) -> ApiResponse[TeacherSchema]:
    container = get_container()
    use_case: CreateTeacherUseCase = container.resolve(CreateTeacherUseCase)
    teacher = use_case.execute(
        first_name=schema.first_name,
        last_name=schema.last_name,
        middle_name=schema.middle_name,
        rank=schema.rank,
    )

    return ApiResponse(
        data=TeacherSchema.from_entity(entity=teacher),
    )


@router.patch(
    "{teacher_uuid}/update_name",
    response=ApiResponse[TeacherSchema],
    operation_id="update_teacher_name",
    auth=jwt_auth_teacher_manager,
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
    response=ApiResponse[TeacherSchema],
    operation_id="update_teacher_rank",
    auth=jwt_auth_teacher_manager,
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
    response=ApiResponse[StatusResponse],
    operation_id="delete_teacher",
    auth=jwt_auth_teacher_manager,
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
