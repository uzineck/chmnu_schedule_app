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
    TeacherNameInSchema,
    TeacherRankInSchema,
    TeacherSchema,
)
from core.apps.common.authentication.bearer import (
    jwt_bearer_admin,
    jwt_bearer_manager,
)
from core.apps.common.cache.service import BaseCacheService
from core.apps.common.cache.timeouts import Timeout
from core.apps.common.exceptions import ServiceException
from core.apps.schedule.filters.teacher import TeacherFilter as TeacherFilterEntity
from core.apps.schedule.use_cases.teacher.create import CreateTeacherUseCase
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
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: GetAllTeachersUseCase = container.resolve(GetAllTeachersUseCase)
    try:
        teachers = use_case.execute()

        cache_key = cache_service.generate_cache_key(
            model_prefix="teacher",
            func_prefix="all",
        )
        items = cache_service.get_cache_value(key=cache_key)
        if not items:
            items = [TeacherSchema.from_entity(obj) for obj in teachers]
            cache_service.set_cache(key=cache_key, value=items, timeout=Timeout.MONTH)

    except ServiceException as e:
        raise HttpError(
            status_code=403,
            message=e.message,
        )
    return ApiResponse(
        data=items,
    )


@router.get(
    "",
    response=ApiResponse[ListPaginatedResponse[TeacherSchema]],
    operation_id="get_teacher_list",
    auth=[jwt_bearer_admin, jwt_bearer_manager],
)
def get_teacher_list(
        request: HttpRequest,
        filters: Query[TeacherFilter],
        pagination_in: Query[PaginationIn],
) -> ApiResponse[ListPaginatedResponse[TeacherSchema]]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: GetTeacherListUseCase = container.resolve(GetTeacherListUseCase)
    try:
        cache_key = cache_service.generate_cache_key(
            model_prefix="teacher",
            func_prefix="list",
            filters=filters,
            pagination_in=pagination_in,
        )
        items = cache_service.get_cache_value(key=cache_key)
        if not items:
            teacher_list, teacher_count = use_case.execute(
                filters=TeacherFilterEntity(
                    first_name=filters.first_name,
                    last_name=filters.last_name,
                    middle_name=filters.middle_name,
                    rank=filters.rank,
                ),
                pagination=pagination_in,
            )
            teacher_list = [TeacherSchema.from_entity(obj) for obj in teacher_list]
            pagination_out = PaginationOut(
                offset=pagination_in.offset,
                limit=pagination_in.limit,
                total=teacher_count,
            )
            items = teacher_list, pagination_out
            cache_service.set_cache(key=cache_key, value=items, timeout=Timeout.DAY)

        teacher_list, pagination_out = items
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=ListPaginatedResponse(
            items=teacher_list,
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
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: GetLessonsForTeacherUseCase = container.resolve(GetLessonsForTeacherUseCase)
    try:
        cache_key = cache_service.generate_cache_key(
            model_prefix="teacher",
            identifier=teacher_uuid,
            func_prefix="lessons",
        )
        teacher_lessons = cache_service.get_cache_value(key=cache_key)
        if not teacher_lessons:
            teacher, lessons, groups = use_case.execute(teacher_uuid=teacher_uuid)
            items = [LessonForTeacherOutSchema.from_entity(lesson, groups.get(lesson.id, [])) for lesson in lessons]
            teacher_lessons = teacher, items
            cache_service.set_cache(key=cache_key, value=teacher_lessons, timeout=Timeout.DAY)

        teacher, lessons = teacher_lessons

    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=TeacherLessonsOutSchema(
            teacher=teacher,
            lessons=lessons,
        ),
    )


@router.post(
    "",
    response=ApiResponse[TeacherSchema],
    operation_id="create_teacher",
    auth=[jwt_bearer_admin, jwt_bearer_manager],
)
def create_teacher(request: HttpRequest, schema: TeacherInSchema) -> ApiResponse[TeacherSchema]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: CreateTeacherUseCase = container.resolve(CreateTeacherUseCase)
    try:
        teacher = use_case.execute(
            first_name=schema.first_name,
            last_name=schema.last_name,
            middle_name=schema.middle_name,
            rank=schema.rank,
        )
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="teacher",
                    func_prefix="all",
                ),
                cache_service.generate_cache_key(
                    model_prefix="teacher",
                    func_prefix="list",
                    filters="*",
                    pagination_in="*",
                ),
            ],
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
    auth=[jwt_bearer_admin, jwt_bearer_manager],
)
def update_teacher_name(
        request: HttpRequest,
        teacher_uuid: str,
        schema: TeacherNameInSchema,
) -> ApiResponse[TeacherSchema]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: UpdateTeacherNameUseCase = container.resolve(UpdateTeacherNameUseCase)
    try:
        teacher = use_case.execute(
            teacher_uuid=teacher_uuid,
            first_name=schema.first_name,
            last_name=schema.last_name,
            middle_name=schema.middle_name,
        )
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="teacher",
                    func_prefix="all",
                ),
                cache_service.generate_cache_key(
                    model_prefix="teacher",
                    func_prefix="list",
                    filters="*",
                    pagination_in="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="teacher",
                    identifier=teacher.uuid,
                    func_prefix="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="group",
                    identifier="*",
                    func_prefix="lessons",
                ),
            ],
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
    auth=[jwt_bearer_admin, jwt_bearer_manager],
)
def update_teacher_rank(
        request: HttpRequest,
        teacher_uuid: str,
        schema: TeacherRankInSchema,
) -> ApiResponse[TeacherSchema]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: UpdateTeacherRankUseCase = container.resolve(UpdateTeacherRankUseCase)
    try:
        teacher = use_case.execute(
            teacher_uuid=teacher_uuid,
            rank=schema.rank,
        )
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="teacher",
                    func_prefix="all",
                ),
                cache_service.generate_cache_key(
                    model_prefix="teacher",
                    func_prefix="list",
                ),
                cache_service.generate_cache_key(
                    model_prefix="teacher",
                    identifier=teacher.uuid,
                    func_prefix="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="group",
                    identifier="*",
                    func_prefix="lessons",
                ),
            ],
        )
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )
    return ApiResponse(
        data=TeacherSchema.from_entity(entity=teacher),
    )
