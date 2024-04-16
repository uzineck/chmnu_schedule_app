from django.http import HttpResponse
from django.http import HttpRequest
from ninja import Router, Query
from ninja.errors import HttpError
from django.db import IntegrityError
from core.api.schemas import ApiResponse
from core.api.v1.schedule.subjects.schemas import SubjectCreateOutSchema, SubjectCreateInSchema, SubjectGetOutSchema, \
    SubjectUpdateInSchema, SubjectUpdateOutSchema
from core.apps.common.authentication import auth_bearer
from core.apps.common.exceptions import ServiceException
from core.api.v1.schedule.subjects.containers import subject_service
from core.api.v1.schedule.subjects.filters import SubjectFilter
from core.apps.schedule.filters.subjects import SubjectFilters as SubjectFilterEntity

router = Router(tags=["Subjects"])


@router.post("create",
             response=ApiResponse[SubjectCreateOutSchema],
             operation_id="create_subject",
             auth=auth_bearer)
def create_subject(request: HttpRequest, schema: SubjectCreateInSchema) -> ApiResponse[SubjectCreateOutSchema]:
    try:
        subject = subject_service.create(title=schema.title)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message
        )

    return ApiResponse(data=SubjectCreateOutSchema(
        title=subject.title,
        slug=subject.slug
    ))


@router.get("",
            response=ApiResponse[SubjectGetOutSchema],
            operation_id="get_subject_by_title")
def get_subject(request: HttpRequest, title: Query[SubjectFilter]) -> ApiResponse[SubjectGetOutSchema]:
    try:
        subject = subject_service.get_subject_by_title(filters=SubjectFilterEntity(search=title.search))
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message
        )

    return ApiResponse(data=SubjectGetOutSchema(
        title=subject.title,
        slug=subject.slug
    ))


@router.patch("",
              response=ApiResponse[SubjectUpdateOutSchema],
              operation_id="update_subject_by_id",
              auth=auth_bearer)
def update_subject(request: HttpRequest, schema: SubjectUpdateInSchema) -> ApiResponse[SubjectUpdateOutSchema]:
    try:
        subject = subject_service.update_subject_by_id(subject_id=schema.subject_id, title=schema.title)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message
        )

    return ApiResponse(data=SubjectUpdateOutSchema(
        title=f"Subject changed successfully: {subject.title}"
    ))

