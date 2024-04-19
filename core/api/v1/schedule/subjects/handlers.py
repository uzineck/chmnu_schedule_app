from django.http import HttpResponse
from django.http import HttpRequest
from ninja import Router, Query
from ninja.errors import HttpError
from django.db import IntegrityError

from core.api.filters import PaginationOut, PaginationIn, SearchFilter
from core.api.schemas import ApiResponse, ListPaginatedResponse, StatusResponse
from core.api.v1.schedule.subjects.schemas import SubjectInSchema, SubjectSchema
from core.apps.common.authentication import auth_bearer
from core.apps.common.exceptions import ServiceException
from core.api.v1.schedule.subjects.containers import subject_service
from core.apps.common.filters import SearchFilter as SearchFiltersEntity

router = Router(tags=["Subjects"])


@router.get("",
            response=ApiResponse[ListPaginatedResponse[SubjectSchema]],
            operation_id="get_subject_list")
def get_subject_list(request: HttpRequest,
                     filters: Query[SearchFilter],
                     pagination_in: Query[PaginationIn]) -> ApiResponse[ListPaginatedResponse[SubjectSchema]]:
    try:
        subject_list = subject_service.get_subject_list(filters=SearchFiltersEntity(search=filters.search),
                                                        pagination=pagination_in)
        subject_count = subject_service.get_subject_count(filters=filters)

        items = [SubjectSchema.from_entity(obj) for obj in subject_list]

        pagination_out = PaginationOut(
            offset=pagination_in.offset,
            limit=pagination_in.limit,
            total=subject_count,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message
        )

    return ApiResponse(data=ListPaginatedResponse(
        items=items,
        pagination=pagination_out
    ))


@router.post("",
             response=ApiResponse[SubjectSchema],
             operation_id="get_or_create_subject",
             auth=auth_bearer)
def get_or_create_subject(request: HttpRequest, schema: SubjectInSchema) -> ApiResponse[SubjectSchema]:
    try:
        subject = subject_service.get_or_create(title=schema.title)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message
        )

    return ApiResponse(data=SubjectSchema(
        id=subject.id,
        title=subject.title,
        slug=subject.slug
    ))


@router.patch("",
              response=ApiResponse[SubjectSchema],
              operation_id="update_subject_by_id",
              auth=auth_bearer)
def update_subject(request: HttpRequest, subject_id: int, schema: SubjectInSchema) -> ApiResponse[SubjectSchema]:
    try:
        subject = subject_service.update_subject_by_id(subject_id=subject_id, title=schema.title)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message
        )

    return ApiResponse(data=SubjectSchema(
        id=subject.id,
        title=subject.title,
        slug=subject.slug
    ))


@router.delete("", response=ApiResponse[StatusResponse],
               operation_id="delete_subject_by_id",
               auth=auth_bearer)
def delete_subject(request: HttpRequest, subject_id: int) -> ApiResponse[StatusResponse]:
    try:
        subject_service.delete_subject_by_id(subject_id=subject_id)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message
        )

    return ApiResponse(data=StatusResponse(
        status=f"Subject deleted successfully"
    ))
