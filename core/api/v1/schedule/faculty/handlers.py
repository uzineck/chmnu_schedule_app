from django.http import HttpRequest
from ninja import (
    Query,
    Router,
)

from core.api.filters import (
    PaginationIn,
    PaginationOut,
    SearchFilter,
)
from core.api.schemas import (
    ApiErrorResponse,
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
    jwt_auth_faculty_manager,
)
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
    response={
        200: ApiResponse[list[FacultySchema]],
        401: ApiErrorResponse,
    },
    operation_id="get_all_faculties",
    auth=jwt_auth,
    summary="List every active faculty",
    description=(
        "Returns the full collection of active faculties — no pagination, no filtering. Intended "
        "for dropdowns and lookups where the caller needs every faculty at once. Use "
        "`get_faculty_list` for paginated / searchable access."
    ),
)
def get_all_faculties(request: HttpRequest) -> ApiResponse[list[FacultySchema]]:
    container = get_container()
    use_case: GetAllFacultiesUseCase = container.resolve(GetAllFacultiesUseCase)
    items = [FacultySchema.from_entity(obj) for obj in use_case.execute()]
    return ApiResponse(
        data=items,
    )


@router.get(
    "",
    response={
        200: ApiResponse[ListPaginatedResponse[FacultySchema]],
        401: ApiErrorResponse,
    },
    operation_id="get_faculty_list",
    auth=jwt_auth,
    summary="Search and paginate faculties",
    description=(
        "Returns a paginated list of active faculties. The `search` query parameter performs a "
        "case-insensitive match against the faculty name and code name."
    ),
)
def get_faculty_list(
    request: HttpRequest,
    filters: Query[SearchFilter],
    pagination_in: Query[PaginationIn],
) -> ApiResponse[ListPaginatedResponse[FacultySchema]]:
    container = get_container()
    use_case: GetFacultyListUseCase = container.resolve(GetFacultyListUseCase)
    item_list, item_count = use_case.execute(
        filters=SearchFilterEntity(search=filters.search),
        pagination_in=pagination_in,
    )
    pagination_out = PaginationOut(
        offset=pagination_in.offset,
        limit=pagination_in.limit,
        total=item_count,
    )

    return ApiResponse(
        data=ListPaginatedResponse(
            items=[FacultySchema.from_entity(obj) for obj in item_list],
            pagination=pagination_out,
        ),
    )


@router.post(
    "",
    response={
        201: ApiResponse[FacultySchema],
        400: ApiErrorResponse,
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        409: ApiErrorResponse,
    },
    operation_id="create_faculty",
    auth=jwt_auth_faculty_manager,
    summary="Create a faculty",
    description=(
        "Registers a new faculty. The `code_name` (short identifier such as `FCST`) must be unique. "
        "Requires ADMIN or FACULTY_MANAGER role."
    ),
)
def create_faculty(
        request: HttpRequest,
        schema: FacultyInSchema,
) -> tuple[int, ApiResponse[FacultySchema]]:
    container = get_container()
    use_case: CreateFacultyUseCase = container.resolve(CreateFacultyUseCase)
    faculty = use_case.execute(name=schema.name, code_name=schema.code_name)
    return 201, ApiResponse(
        data=FacultySchema.from_entity(entity=faculty),
    )


@router.patch(
    "{faculty_uuid}/update_name",
    response={
        200: ApiResponse[FacultySchema],
        400: ApiErrorResponse,
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
    },
    operation_id="update_faculty_name",
    auth=jwt_auth_faculty_manager,
    summary="Rename a faculty",
    description="Updates only the long `name` of a faculty. The `code_name` is left untouched.",
)
def update_faculty_name(
        request: HttpRequest,
        faculty_uuid: str,
        schema: FacultyNameSchema,
) -> ApiResponse[FacultySchema]:
    container = get_container()
    use_case: UpdateFacultyNameUseCase = container.resolve(UpdateFacultyNameUseCase)
    faculty = use_case.execute(faculty_uuid=faculty_uuid, name=schema.name)
    return ApiResponse(
        data=FacultySchema.from_entity(entity=faculty),
    )


@router.patch(
    "{faculty_uuid}/update_code_name",
    response={
        200: ApiResponse[FacultySchema],
        400: ApiErrorResponse,
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
        409: ApiErrorResponse,
    },
    operation_id="update_faculty_code_name",
    auth=jwt_auth_faculty_manager,
    summary="Change a faculty's code name",
    description=(
        "Updates only the short `code_name` identifier. Returns 409 if another faculty already "
        "owns the new code name."
    ),
)
def update_faculty_code_name(
        request: HttpRequest,
        faculty_uuid: str,
        schema: FacultyCodeNameSchema,
) -> ApiResponse[FacultySchema]:
    container = get_container()
    use_case: UpdateFacultyCodeNameUseCase = container.resolve(UpdateFacultyCodeNameUseCase)
    faculty = use_case.execute(faculty_uuid=faculty_uuid, code_name=schema.code_name)
    return ApiResponse(
        data=FacultySchema.from_entity(entity=faculty),
    )


@router.delete(
    "{faculty_uuid}",
    response={
        200: ApiResponse[StatusResponse],
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
        409: ApiErrorResponse,
    },
    operation_id="delete_faculty",
    auth=jwt_auth_faculty_manager,
    summary="Soft-delete a faculty",
    description=(
        "Marks the faculty inactive. Returns 409 if the faculty is still referenced by any active "
        "group. Requires ADMIN or FACULTY_MANAGER role."
    ),
)
def delete_faculty(
    request: HttpRequest,
    faculty_uuid: str,
) -> ApiResponse[StatusResponse]:
    container = get_container()
    use_case: DeleteFacultyUseCase = container.resolve(DeleteFacultyUseCase)
    use_case.execute(faculty_uuid=faculty_uuid)

    return ApiResponse(
        data=StatusResponse(status="Faculty deleted successfully"),
    )
