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
)
from core.api.v1.schedule.faculty.schemas import (
    FacultyCodeNameSchema,
    FacultyInSchema,
    FacultyNameSchema,
    FacultySchema,
)
from core.apps.common.authentication.bearer import jwt_bearer_admin
from core.apps.common.exceptions import ServiceException
from core.apps.common.filters import SearchFilter as SearchFilterEntity
from core.apps.schedule.use_cases.faculty.create import CreateFacultyUseCase
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
)
def get_all_faculties(request: HttpRequest) -> ApiResponse[list[FacultySchema]]:
    container = get_container()
    use_case: GetAllFacultiesUseCase = container.resolve(GetAllFacultiesUseCase)
    try:
        faculties = use_case.execute()
        items = [FacultySchema.from_entity(obj) for obj in faculties]
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
    response=ApiResponse[ListPaginatedResponse[FacultySchema]],
    operation_id="get_faculty_list",
)
def get_faculty_list(
    request: HttpRequest,
    filters: Query[SearchFilter],
    pagination_in: Query[PaginationIn],
) -> ApiResponse[ListPaginatedResponse[FacultySchema]]:
    container = get_container()
    use_case: GetFacultyListUseCase = container.resolve(GetFacultyListUseCase)
    try:
        faculty_list, faculty_count = use_case.execute(
            filters=SearchFilterEntity(search=filters.search),
            pagination=pagination_in,
        )
        items = [FacultySchema.from_entity(obj) for obj in faculty_list]
        pagination_out = PaginationOut(
            offset=pagination_in.offset,
            limit=pagination_in.limit,
            total=faculty_count,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=403,
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
    response=ApiResponse[FacultySchema],
    operation_id="create_faculty",
    auth=jwt_bearer_admin,
)
def create_faculty(
        request: HttpRequest,
        schema: FacultyInSchema,
) -> ApiResponse[FacultySchema]:
    container = get_container()
    use_case: CreateFacultyUseCase = container.resolve(CreateFacultyUseCase)
    try:
        faculty = use_case.execute(name=schema.name, code_name=schema.code_name)
    except ServiceException as e:
        raise HttpError(
            status_code=403,
            message=e.message,
        )
    return ApiResponse(
        data=FacultySchema.from_entity(entity=faculty),
    )


@router.post(
    "{faculty_uuid}/update_name",
    response=ApiResponse[FacultySchema],
    operation_id="update_faculty_name",
    auth=jwt_bearer_admin,
)
def update_faculty_name(
        request: HttpRequest,
        faculty_uuid: str,
        schema: FacultyNameSchema,
) -> ApiResponse[FacultySchema]:
    container = get_container()
    use_case: UpdateFacultyNameUseCase = container.resolve(UpdateFacultyNameUseCase)
    try:
        faculty = use_case.execute(faculty_uuid=faculty_uuid, name=schema.name)
    except ServiceException as e:
        raise HttpError(
            status_code=403,
            message=e.message,
        )
    return ApiResponse(
        data=FacultySchema.from_entity(entity=faculty),
    )


@router.post(
    "{faculty_uuid}/update_code_name",
    response=ApiResponse[FacultySchema],
    operation_id="update_faculty_code_name",
    auth=jwt_bearer_admin,
)
def update_faculty_code_name(
        request: HttpRequest,
        faculty_uuid: str,
        schema: FacultyCodeNameSchema,
) -> ApiResponse[FacultySchema]:
    container = get_container()
    use_case: UpdateFacultyCodeNameUseCase = container.resolve(UpdateFacultyCodeNameUseCase)
    try:
        faculty = use_case.execute(faculty_uuid=faculty_uuid, code_name=schema.code_name)
    except ServiceException as e:
        raise HttpError(
            status_code=403,
            message=e.message,
        )
    return ApiResponse(
        data=FacultySchema.from_entity(entity=faculty),
    )
