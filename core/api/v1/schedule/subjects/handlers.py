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
    UpdateSubjectTitleSchema,
)
from core.apps.common.authentication.bearer import jwt_bearer_admin
from core.apps.common.exceptions import ServiceException
from core.apps.common.filters import SearchFilter as SearchFiltersEntity
from core.apps.schedule.services.subject import BaseSubjectService
from core.project.containers.containers import get_container


router = Router(tags=["Subjects"])


@router.get(
    "",
    response=ApiResponse[ListPaginatedResponse[SubjectSchema]],
    operation_id="get_subject_list",
)
def get_subject_list(
    request: HttpRequest,
    filters: Query[SearchFilter],
    pagination_in: Query[PaginationIn],
) -> ApiResponse[ListPaginatedResponse[SubjectSchema]]:
    container = get_container()
    service: BaseSubjectService = container.resolve(BaseSubjectService)
    try:
        subject_list = service.get_subject_list(
            filters=SearchFiltersEntity(search=filters.search),
            pagination=pagination_in,
        )
        subject_count = service.get_subject_count(filters=filters)

        items = [SubjectSchema.from_entity(obj) for obj in subject_list]

        pagination_out = PaginationOut(
            offset=pagination_in.offset,
            limit=pagination_in.limit,
            total=subject_count,
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


@router.post(
    "",
    response=ApiResponse[SubjectSchema],
    operation_id="get_or_create_subject",
    auth=jwt_bearer_admin,
)
def get_or_create_subject(request: HttpRequest, schema: SubjectInSchema) -> ApiResponse[SubjectSchema]:
    container = get_container()
    service: BaseSubjectService = container.resolve(BaseSubjectService)
    try:
        subject = service.get_or_create(title=schema.title)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=SubjectSchema.from_entity(entity=subject),
    )


@router.patch(
    "{subject_uuid}",
    response=ApiResponse[SubjectSchema],
    operation_id="update_subject_by_uuid",
    auth=jwt_bearer_admin,
)
def update_subject(request: HttpRequest, schema: UpdateSubjectTitleSchema) -> ApiResponse[SubjectSchema]:
    container = get_container()
    service: BaseSubjectService = container.resolve(BaseSubjectService)
    try:
        subject = service.update_subject_by_uuid(subject_uuid=schema.subject_uuid, title=schema.new_title)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=SubjectSchema.from_entity(entity=subject),
    )


@router.delete(
    "{subject_uuid}",
    response=ApiResponse[StatusResponse],
    operation_id="delete_subject_by_uuid",
    auth=jwt_bearer_admin,
)
def delete_subject(request: HttpRequest, subject_uuid: str) -> ApiResponse[StatusResponse]:
    container = get_container()
    service: BaseSubjectService = container.resolve(BaseSubjectService)
    try:
        service.delete_subject_by_uuid(subject_uuid=subject_uuid)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=StatusResponse(
            status="Subject deleted successfully",
        ),
    )

