from django.http import HttpResponse
from django.http import HttpRequest
from ninja import Router, Query
from ninja.errors import HttpError

from core.api.filters import PaginationIn, PaginationOut
from core.api.schemas import ApiResponse, ListPaginatedResponse
from core.api.v1.schedule.teachers.schemas import TeacherInSchema, TeacherSchema, TeacherUpdateSubjectsInSchema
from core.apps.common.authentication.bearer import jwt_bearer
from core.apps.common.exceptions import ServiceException
from core.api.v1.schedule.teachers.filters import TeacherFilter
from core.apps.schedule.filters.teacher import TeacherFilter as TeacherFilterEntity
from core.apps.schedule.models import Teacher
from core.apps.schedule.services.teachers import BaseTeacherService
from core.project.containers import get_container

router = Router(tags=["Teachers"])


@router.get("",
            response=ApiResponse[ListPaginatedResponse[TeacherSchema]],
            operation_id="get_teacher_list")
def get_teacher_list(request: HttpRequest,
                     filters: Query[TeacherFilter],
                     pagination_in: Query[PaginationIn]) -> ApiResponse[ListPaginatedResponse[TeacherSchema]]:
    container = get_container()
    service = container.resolve(BaseTeacherService)
    try:
        teacher_list = service.get_teacher_list(filters=TeacherFilterEntity(name=filters.name,
                                                                            rank=filters.rank),
                                                pagination=pagination_in)
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
            message=e.message
        )

    return ApiResponse(data=ListPaginatedResponse(
        items=items,
        pagination=pagination_out
    ))


@router.post("",
             response=ApiResponse[TeacherSchema],
             operation_id="get_or_create_teacher",
             auth=jwt_bearer)
def get_or_create_teacher(request: HttpRequest, schema: TeacherInSchema) -> ApiResponse[TeacherSchema]:
    container = get_container()
    service = container.resolve(BaseTeacherService)
    try:
        teacher = service.get_or_create(first_name=schema.first_name,
                                        last_name=schema.last_name,
                                        middle_name=schema.middle_name,
                                        rank=schema.rank)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message
        )

    return ApiResponse(data=TeacherSchema(
        id=teacher.id,
        last_name=teacher.last_name,
        first_name=teacher.first_name,
        middle_name=teacher.middle_name,
        rank=teacher.rank,
        subjects=teacher.subjects
    ))


@router.patch("{teacher_id}/update",
              response=ApiResponse[TeacherSchema],
              operation_id="update_teacher",
              auth=jwt_bearer)
def update_teacher(request: HttpRequest,
                   teacher_id: int,
                   schema: TeacherInSchema) -> ApiResponse[TeacherSchema]:
    container = get_container()
    service = container.resolve(BaseTeacherService)
    try:
        teacher = service.update_teacher_by_id(teacher_id=teacher_id,
                                               first_name=schema.first_name,
                                               last_name=schema.last_name,
                                               middle_name=schema.middle_name,
                                               rank=schema.rank)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message
        )

    return ApiResponse(data=TeacherSchema(
        id=teacher.id,
        last_name=teacher.last_name,
        first_name=teacher.first_name,
        middle_name=teacher.middle_name,
        rank=teacher.rank,
        subjects=teacher.subjects
    ))


@router.patch("{teacher_id}/add_subjects",
              response=ApiResponse[TeacherSchema],
              operation_id="add_teacher_subjects",
              auth=jwt_bearer)
def add_teacher_subjects(request: HttpRequest,
                         teacher_id: int,
                         schema: TeacherUpdateSubjectsInSchema) -> ApiResponse[TeacherSchema]:
    container = get_container()
    service = container.resolve(BaseTeacherService)
    try:
        teacher = service.add_teacher_subject(teacher_id=teacher_id, subject_id=schema.subject_id)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message
        )

    return ApiResponse(data=TeacherSchema(
        id=teacher.id,
        last_name=teacher.last_name,
        first_name=teacher.first_name,
        middle_name=teacher.middle_name,
        rank=teacher.rank,
        subjects=teacher.subjects
    ))


@router.patch("{teacher_id}/remove_subjects",
              response=ApiResponse[TeacherSchema],
              operation_id="remove_teacher_subjects",
              auth=jwt_bearer)
def remove_teacher_subjects(request: HttpRequest,
                            teacher_id: int,
                            schema: TeacherUpdateSubjectsInSchema) -> ApiResponse[TeacherSchema]:
    container = get_container()
    service = container.resolve(BaseTeacherService)
    try:
        teacher = service.remove_teacher_subject(teacher_id=teacher_id, subject_id=schema.subject_id)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message
        )

    return ApiResponse(data=TeacherSchema(
        id=teacher.id,
        last_name=teacher.last_name,
        first_name=teacher.first_name,
        middle_name=teacher.middle_name,
        rank=teacher.rank,
        subjects=teacher.subjects
    ))