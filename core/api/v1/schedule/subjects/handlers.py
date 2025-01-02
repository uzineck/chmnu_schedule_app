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
from core.api.v1.schedule.subjects.schemas import (
    SubjectInSchema,
    SubjectSchema,
)
from core.apps.common.authentication.bearer import (
    jwt_bearer,
    jwt_bearer_admin,
    jwt_bearer_manager,
)
from core.apps.common.cache.service import BaseCacheService
from core.apps.common.cache.timeouts import Timeout
from core.apps.common.exceptions import ServiceException
from core.apps.common.filters import SearchFilter as SearchFilterEntity
from core.apps.schedule.use_cases.subject.create import CreateSubjectUseCase
from core.apps.schedule.use_cases.subject.delete import DeleteSubjectUseCase
from core.apps.schedule.use_cases.subject.get_all import GetAllSubjectsUseCase
from core.apps.schedule.use_cases.subject.get_list import GetSubjectListUseCase
from core.apps.schedule.use_cases.subject.update import UpdateSubjectUseCase
from core.project.containers.containers import get_container


router = Router(tags=["Subjects"])


@router.get(
    'all',
    response=ApiResponse[list[SubjectSchema]],
    operation_id='get_all_subjects',
    auth=jwt_bearer,
)
def get_all_subjects(request: HttpRequest) -> ApiResponse[list[SubjectSchema]]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: GetAllSubjectsUseCase = container.resolve(GetAllSubjectsUseCase)
    try:
        cache_key = cache_service.generate_cache_key(
            model_prefix="subject",
            func_prefix="all",
        )
        items = cache_service.get_cache_value(key=cache_key)
        if not items:
            items = [SubjectSchema.from_entity(obj) for obj in use_case.execute()]
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
    response=ApiResponse[ListPaginatedResponse[SubjectSchema]],
    operation_id="get_subject_list",
    auth=jwt_bearer,
)
def get_subject_list(
    request: HttpRequest,
    filters: Query[SearchFilter],
    pagination_in: Query[PaginationIn],
) -> ApiResponse[ListPaginatedResponse[SubjectSchema]]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: GetSubjectListUseCase = container.resolve(GetSubjectListUseCase)
    try:
        cache_key = cache_service.generate_cache_key(
            model_prefix="subject",
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
            items=[SubjectSchema.from_entity(obj) for obj in item_list],
            pagination=pagination_out,
        ),
    )


@router.post(
    "",
    response={201: ApiResponse[SubjectSchema]},
    operation_id="create_subject",
    auth=[jwt_bearer_admin, jwt_bearer_manager],
)
def create(request: HttpRequest, schema: SubjectInSchema) -> ApiResponse[SubjectSchema]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: CreateSubjectUseCase = container.resolve(CreateSubjectUseCase)
    try:
        subject = use_case.execute(title=schema.title)
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="subject",
                    func_prefix="all",
                ),
                cache_service.generate_cache_key(
                    model_prefix="subject",
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
        data=SubjectSchema.from_entity(entity=subject),
    )


@router.patch(
    "{subject_uuid}/update",
    response=ApiResponse[SubjectSchema],
    operation_id="update_subject",
    auth=[jwt_bearer_admin, jwt_bearer_manager],
)
def update_subject(request: HttpRequest, subject_uuid: str, schema: SubjectInSchema) -> ApiResponse[SubjectSchema]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: UpdateSubjectUseCase = container.resolve(UpdateSubjectUseCase)
    try:
        subject = use_case.execute(subject_uuid=subject_uuid, title=schema.title)
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="subject",
                    func_prefix="all",
                ),
                cache_service.generate_cache_key(
                    model_prefix="subject",
                    func_prefix="list",
                    filters="*",
                    pagination_in="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="group",
                    identifier="*",
                    func_prefix="lessons",
                    filters="*",
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
        data=SubjectSchema.from_entity(entity=subject),
    )


@router.delete(
    "{subject_uuid}",
    response=ApiResponse[StatusResponse],
    operation_id="delete_subject",
    auth=[jwt_bearer_admin, jwt_bearer_manager],
)
def delete_subject(
    request: HttpRequest,
    subject_uuid: str,
) -> ApiResponse[StatusResponse]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: DeleteSubjectUseCase = container.resolve(DeleteSubjectUseCase)
    try:
        use_case.execute(subject_uuid=subject_uuid)
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="subject",
                    func_prefix="all",
                ),
                cache_service.generate_cache_key(
                    model_prefix="subject",
                    func_prefix="list",
                    filters="*",
                    pagination_in="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="group",
                    identifier="*",
                    func_prefix="lessons",
                    filters="*",
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
        data=StatusResponse(status="Subject deleted successfully"),
    )
