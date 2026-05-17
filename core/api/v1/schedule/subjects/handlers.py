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
    ApiResponse,
    ListPaginatedResponse,
    StatusResponse,
)
from core.api.v1.schedule.subjects.schemas import (
    SubjectInSchema,
    SubjectSchema,
)
from core.apps.common.authentication.ninja_auth import (
    jwt_auth,
    jwt_auth_subject_manager,
)
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
    auth=jwt_auth,
)
def get_all_subjects(request: HttpRequest) -> ApiResponse[list[SubjectSchema]]:
    container = get_container()
    use_case: GetAllSubjectsUseCase = container.resolve(GetAllSubjectsUseCase)
    items = [SubjectSchema.from_entity(obj) for obj in use_case.execute()]
    return ApiResponse(
        data=items,
    )


@router.get(
    "",
    response=ApiResponse[ListPaginatedResponse[SubjectSchema]],
    operation_id="get_subject_list",
    auth=jwt_auth,
)
def get_subject_list(
    request: HttpRequest,
    filters: Query[SearchFilter],
    pagination_in: Query[PaginationIn],
) -> ApiResponse[ListPaginatedResponse[SubjectSchema]]:
    container = get_container()
    use_case: GetSubjectListUseCase = container.resolve(GetSubjectListUseCase)
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
            items=[SubjectSchema.from_entity(obj) for obj in item_list],
            pagination=pagination_out,
        ),
    )


@router.post(
    "",
    response={201: ApiResponse[SubjectSchema]},
    operation_id="create_subject",
    auth=jwt_auth_subject_manager,
)
def create(request: HttpRequest, schema: SubjectInSchema) -> ApiResponse[SubjectSchema]:
    container = get_container()
    use_case: CreateSubjectUseCase = container.resolve(CreateSubjectUseCase)
    subject = use_case.execute(title=schema.title)

    return ApiResponse(
        data=SubjectSchema.from_entity(entity=subject),
    )


@router.patch(
    "{subject_uuid}/update",
    response=ApiResponse[SubjectSchema],
    operation_id="update_subject",
    auth=jwt_auth_subject_manager,
)
def update_subject(request: HttpRequest, subject_uuid: str, schema: SubjectInSchema) -> ApiResponse[SubjectSchema]:
    container = get_container()
    use_case: UpdateSubjectUseCase = container.resolve(UpdateSubjectUseCase)
    subject = use_case.execute(subject_uuid=subject_uuid, title=schema.title)

    return ApiResponse(
        data=SubjectSchema.from_entity(entity=subject),
    )


@router.delete(
    "{subject_uuid}",
    response=ApiResponse[StatusResponse],
    operation_id="delete_subject",
    auth=jwt_auth_subject_manager,
)
def delete_subject(
    request: HttpRequest,
    subject_uuid: str,
) -> ApiResponse[StatusResponse]:
    container = get_container()
    use_case: DeleteSubjectUseCase = container.resolve(DeleteSubjectUseCase)
    use_case.execute(subject_uuid=subject_uuid)

    return ApiResponse(
        data=StatusResponse(status="Subject deleted successfully"),
    )
