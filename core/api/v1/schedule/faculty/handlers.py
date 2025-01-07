from django.http import HttpRequest
from ninja import (
    Query,
    Router,
)
from ninja.errors import HttpError

from core.api.filters import (
    PaginationIn,
    PaginationOut,
    SearchFilter,
)
from core.api.schemas import (
    ApiResponse,
    ListPaginatedResponse,
    StatusResponse,
)
from core.api.v1.schedule.faculty.schemas import (
    FacultyCodeNameSchema,
    FacultyInSchema,
    FacultyNameSchema,
    FacultySchema,
)
from core.apps.common.authentication.ninja_auth import (
    jwt_auth,
    jwt_auth_admin,
    jwt_auth_manager,
)
from core.apps.common.cache.service import BaseCacheService
from core.apps.common.cache.timeouts import Timeout
from core.apps.common.exceptions import ServiceException
from core.apps.common.filters import SearchFilter as SearchFilterEntity
from core.apps.schedule.use_cases.faculty.create import CreateFacultyUseCase
from core.apps.schedule.use_cases.faculty.delete import DeleteFacultyUseCase
from core.apps.schedule.use_cases.faculty.get_all import GetAllFacultiesUseCase
from core.apps.schedule.use_cases.faculty.get_list import GetFacultyListUseCase
from core.apps.schedule.use_cases.faculty.update_code_name import UpdateFacultyCodeNameUseCase
from core.apps.schedule.use_cases.faculty.update_name import UpdateFacultyNameUseCase
from core.project.containers.containers import get_container


router = Router(tags=['Faculty'])


@router.get(
    "all",
    response=ApiResponse[list[FacultySchema]],
    operation_id="get_all_faculties",
    auth=jwt_auth,
)
def get_all_faculties(request: HttpRequest) -> ApiResponse[list[FacultySchema]]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: GetAllFacultiesUseCase = container.resolve(GetAllFacultiesUseCase)
    try:
        cache_key = cache_service.generate_cache_key(
            model_prefix="faculty",
            func_prefix="all",
        )
        items = cache_service.get_cache_value(key=cache_key)
        if not items:
            items = [FacultySchema.from_entity(obj) for obj in use_case.execute()]
            cache_service.set_cache(key=cache_key, value=items, timeout=Timeout.MONTH)

    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )
    return ApiResponse(
        data=items,
    )


@router.get(
    "",
    response=ApiResponse[ListPaginatedResponse[FacultySchema]],
    operation_id="get_faculty_list",
    auth=jwt_auth,
)
def get_faculty_list(
    request: HttpRequest,
    filters: Query[SearchFilter],
    pagination_in: Query[PaginationIn],
) -> ApiResponse[ListPaginatedResponse[FacultySchema]]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: GetFacultyListUseCase = container.resolve(GetFacultyListUseCase)
    try:
        cache_key = cache_service.generate_cache_key(
            model_prefix="faculty",
            func_prefix="list",
            filters=filters,
            pagination_in=pagination_in,
        )
        items = cache_service.get_cache_value(key=cache_key)
        if not items:
            item_list, item_count = use_case.execute(
                filters=SearchFilterEntity(search=filters.search),
                pagination=pagination_in,
            )
            pagination_out = PaginationOut(
                offset=pagination_in.offset,
                limit=pagination_in.limit,
                total=item_count,
            )
            items = item_list, pagination_out
            cache_service.set_cache(key=cache_key, value=items, timeout=Timeout.DAY)

        item_list, pagination_out = items
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )

    return ApiResponse(
        data=ListPaginatedResponse(
            items=[FacultySchema.from_entity(obj) for obj in item_list],
            pagination=pagination_out,
        ),
    )


@router.post(
    "",
    response={201: ApiResponse[FacultySchema]},
    operation_id="create_faculty",
    auth=[jwt_auth_admin, jwt_auth_manager],
)
def create_faculty(
        request: HttpRequest,
        schema: FacultyInSchema,
) -> ApiResponse[FacultySchema]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: CreateFacultyUseCase = container.resolve(CreateFacultyUseCase)
    try:
        faculty = use_case.execute(name=schema.name, code_name=schema.code_name)
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="faculty",
                    func_prefix="all",
                ),
                cache_service.generate_cache_key(
                    model_prefix="faculty",
                    func_prefix="list",
                    filters="*",
                    pagination_in="*",
                ),
            ],
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )
    return ApiResponse(
        data=FacultySchema.from_entity(entity=faculty),
    )


@router.post(
    "{faculty_uuid}/update_name",
    response=ApiResponse[FacultySchema],
    operation_id="update_faculty_name",
    auth=[jwt_auth_admin, jwt_auth_manager],
)
def update_faculty_name(
        request: HttpRequest,
        faculty_uuid: str,
        schema: FacultyNameSchema,
) -> ApiResponse[FacultySchema]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: UpdateFacultyNameUseCase = container.resolve(UpdateFacultyNameUseCase)
    try:
        faculty = use_case.execute(faculty_uuid=faculty_uuid, name=schema.name)
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="faculty",
                    func_prefix="all",
                ),
                cache_service.generate_cache_key(
                    model_prefix="faculty",
                    func_prefix="list",
                    filters="*",
                    pagination_in="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="group",
                    func_prefix="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="teacher",
                    identifier="*",
                    func_prefix="lessons",
                    filters="*",
                ),
            ],
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )
    return ApiResponse(
        data=FacultySchema.from_entity(entity=faculty),
    )


@router.post(
    "{faculty_uuid}/update_code_name",
    response=ApiResponse[FacultySchema],
    operation_id="update_faculty_code_name",
    auth=[jwt_auth_admin, jwt_auth_manager],
)
def update_faculty_code_name(
        request: HttpRequest,
        faculty_uuid: str,
        schema: FacultyCodeNameSchema,
) -> ApiResponse[FacultySchema]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: UpdateFacultyCodeNameUseCase = container.resolve(UpdateFacultyCodeNameUseCase)
    try:
        faculty = use_case.execute(faculty_uuid=faculty_uuid, code_name=schema.code_name)
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="faculty",
                    func_prefix="all",
                ),
                cache_service.generate_cache_key(
                    model_prefix="faculty",
                    func_prefix="list",
                    filters="*",
                    pagination_in="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="group",
                    func_prefix="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="teacher",
                    identifier="*",
                    func_prefix="lessons",
                    filters="*",
                ),
            ],
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )
    return ApiResponse(
        data=FacultySchema.from_entity(entity=faculty),
    )


@router.delete(
    "{faculty_uuid}",
    response=ApiResponse[StatusResponse],
    operation_id="delete_faculty",
    auth=[jwt_auth_admin, jwt_auth_manager],
)
def delete_faculty(
    request: HttpRequest,
    faculty_uuid: str,
) -> ApiResponse[StatusResponse]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: DeleteFacultyUseCase = container.resolve(DeleteFacultyUseCase)
    try:
        use_case.execute(faculty_uuid=faculty_uuid)
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="faculty",
                    func_prefix="all",
                ),
                cache_service.generate_cache_key(
                    model_prefix="faculty",
                    func_prefix="list",
                    filters="*",
                    pagination_in="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="group",
                    identifier="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="teacher",
                    identifier="*",
                    func_prefix="lessons",
                    filters="*",
                ),
            ],
        )

    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )

    return ApiResponse(
        data=StatusResponse(status="Faculty deleted successfully"),
    )
