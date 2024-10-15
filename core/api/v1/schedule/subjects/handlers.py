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
from core.api.v1.schedule.subjects.schemas import (
    SubjectInSchema,
    SubjectSchema,
)
from core.apps.common.authentication.bearer import jwt_bearer_admin
from core.apps.common.exceptions import ServiceException
from core.apps.common.filters import SearchFilter as SearchFilterEntity
from core.apps.schedule.use_cases.subject.create import CreateSubjectUseCase
from core.apps.schedule.use_cases.subject.get_all import GetAllSubjectsUseCase
from core.apps.schedule.use_cases.subject.get_list import GetSubjectListUseCase
from core.apps.schedule.use_cases.subject.update import UpdateSubjectUseCase
from core.project.containers.containers import get_container


router = Router(tags=["Subjects"])


@router.get(
    'all',
    response=ApiResponse[list[SubjectSchema]],
    operation_id='get_all_subjects',

)
def get_all_subjects(request: HttpRequest) -> ApiResponse[list[SubjectSchema]]:
    container = get_container()
    use_case: GetAllSubjectsUseCase = container.resolve(GetAllSubjectsUseCase)
    try:
        subjects = use_case.execute()
        items = [SubjectSchema.from_entity(obj) for obj in subjects]
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
    response=ApiResponse[ListPaginatedResponse[SubjectSchema]],
    operation_id="get_subject_list",
)
def get_subject_list(
    request: HttpRequest,
    filters: Query[SearchFilter],
    pagination_in: Query[PaginationIn],
) -> ApiResponse[ListPaginatedResponse[SubjectSchema]]:
    container = get_container()
    use_case: GetSubjectListUseCase = container.resolve(GetSubjectListUseCase)
    try:
        subject_list, subject_count = use_case.execute(
            filters=SearchFilterEntity(search=filters.search),
            pagination=pagination_in,
        )

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
    operation_id="create_subject",
    auth=jwt_bearer_admin,
)
def create(request: HttpRequest, schema: SubjectInSchema) -> ApiResponse[SubjectSchema]:
    container = get_container()
    use_case: CreateSubjectUseCase = container.resolve(CreateSubjectUseCase)
    try:
        subject = use_case.execute(title=schema.title)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=SubjectSchema.from_entity(entity=subject),
    )


@router.patch(
    "{subject_uuid}/update",
    response=ApiResponse[SubjectSchema],
    operation_id="update_subject",
    auth=jwt_bearer_admin,
)
def update_subject(request: HttpRequest, subject_uuid: str, schema: SubjectInSchema) -> ApiResponse[SubjectSchema]:
    container = get_container()
    use_case: UpdateSubjectUseCase = container.resolve(UpdateSubjectUseCase)
    try:
        subject = use_case.execute(subject_uuid=subject_uuid, title=schema.title)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=SubjectSchema.from_entity(entity=subject),
    )
