from django.http import HttpRequest
from ninja import (
    Query,
    Router,
)
from ninja.errors import HttpError

from typing import Union

from core.api.schemas import (
    ApiResponse,
    StatusResponse,
)
from core.api.v1.clients.schemas import ClientSchemaPrivate
from core.api.v1.schedule.groups.filters import GroupFilter
from core.api.v1.schedule.groups.schemas import (
    CreateGroupSchema,
    GroupLessonsOutSchema,
    GroupSchemaWithHeadman,
    GroupUuidNumberOutSchema,
    UpdateGroupHeadmanSchema,
)
from core.apps.clients.services.client import BaseClientService
from core.apps.clients.usecases.headman.get_headman_info import GetHeadmanInfoUseCase
from core.apps.common.authentication.bearer import (
    jwt_bearer_admin,
    jwt_bearer_headman,
)
from core.apps.common.exceptions import (
    JWTKeyParsingException,
    ServiceException,
)
from core.apps.common.models import Subgroup
from core.apps.schedule.filters.group import GroupLessonFilter as GroupFilterEntity
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.use_cases.group.admin_add_lesson_to_group import AdminAddLessonToGroupUseCase
from core.apps.schedule.use_cases.group.admin_remove_lesson_from_group import AdminRemoveLessonFromGroupUseCase
from core.apps.schedule.use_cases.group.create_group import CreateGroupUseCase
from core.apps.schedule.use_cases.group.get_group_info import GetGroupInfoUseCase
from core.apps.schedule.use_cases.group.get_group_lessons import GetGroupLessonsUseCase
from core.apps.schedule.use_cases.group.headman_add_lesson_to_group import HeadmanAddLessonToGroupUseCase
from core.apps.schedule.use_cases.group.headman_remove_lesson_from_group import HeadmanRemoveLessonFromGroupUseCase
from core.apps.schedule.use_cases.group.update_headman import UpdateGroupHeadmanUseCase
from core.project.containers.containers import get_container


router = Router(tags=['Group'])


@router.get(
    'all',
    response=ApiResponse,
    operation_id='get_all_groups',

)
def get_all_groups(request: HttpRequest) -> ApiResponse:
    container = get_container()
    service: BaseGroupService = container.resolve(BaseGroupService)
    groups = service.get_all_groups()
    items = [GroupUuidNumberOutSchema.from_entity(group) for group in groups]

    return ApiResponse(
        data=items,
    )


@router.get(
    "{group_uuid}/lessons",
    response=ApiResponse[GroupLessonsOutSchema],
    operation_id="get_group_lessons",
)
def get_group_lessons(
        request: HttpRequest,
        group_uuid: str,
        filters: Query[GroupFilter],
) -> ApiResponse[GroupLessonsOutSchema]:
    container = get_container()
    use_case: GetGroupLessonsUseCase = container.resolve(GetGroupLessonsUseCase)
    try:
        group_lesson_filter_entity = GroupFilterEntity(subgroup=filters.subgroup, is_even=filters.is_even)
        group, lessons = use_case.execute(
            group_uuid=group_uuid,
            filters=group_lesson_filter_entity,
        )

    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=GroupLessonsOutSchema.from_entity_with_lesson_entities(
            group_entity=group,
            lesson_entities=lessons,
            subgroup=group_lesson_filter_entity.subgroup,
        ),
    )


@router.get(
    "{group_uuid}/info",
    response=ApiResponse[GroupSchemaWithHeadman],
    operation_id="get_group_info",
    auth=jwt_bearer_admin,
)
def get_group_info(
        request: HttpRequest,
        group_uuid: str,
) -> ApiResponse[GroupSchemaWithHeadman]:
    container = get_container()
    use_case: GetGroupInfoUseCase = container.resolve(GetGroupInfoUseCase)

    try:
        group = use_case.execute(group_uuid=group_uuid)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=GroupSchemaWithHeadman.from_entity(group),
    )


@router.get(
    "get_headman_info",
    response=ApiResponse[Union[GroupSchemaWithHeadman, ClientSchemaPrivate]],
    operation_id='get_headman_info',
    auth=jwt_bearer_admin,
)
def get_headman_info(
        request: HttpRequest,
        headman_email: str,
) -> ApiResponse[Union[GroupSchemaWithHeadman, ClientSchemaPrivate]]:
    container = get_container()
    use_case: GetHeadmanInfoUseCase = container.resolve(GetHeadmanInfoUseCase)
    try:
        group, headman = use_case.execute(
            email=headman_email,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )
    if group is None:
        return ApiResponse(
            data=ClientSchemaPrivate.from_entity(client=headman),
        )
    else:
        return ApiResponse(
            data=GroupSchemaWithHeadman.from_entity(entity=group),
        )


@router.post('', response=ApiResponse[GroupSchemaWithHeadman], operation_id='create_group', auth=jwt_bearer_admin)
def create_group(request: HttpRequest, schema: CreateGroupSchema) -> ApiResponse[GroupSchemaWithHeadman]:
    container = get_container()
    use_case: CreateGroupUseCase = container.resolve(CreateGroupUseCase)
    try:
        group = use_case.execute(
            group_number=schema.number,
            faculty_uuid=schema.faculty_uuid,
            headman_email=schema.headman_email,
            has_subgroups=schema.has_subgroups,
        )

    except ServiceException as e:
        raise HttpError(
            status_code=404,
            message=e.message,
        )

    return ApiResponse(
        data=GroupSchemaWithHeadman.from_entity(entity=group),
    )


@router.patch(
    "update_group_headman",
    response=ApiResponse[GroupSchemaWithHeadman],
    operation_id='update_group_headman',
    auth=jwt_bearer_admin,
)
def update_group_headman(request: HttpRequest, schema: UpdateGroupHeadmanSchema) -> ApiResponse[GroupSchemaWithHeadman]:
    container = get_container()
    use_case: UpdateGroupHeadmanUseCase = container.resolve(UpdateGroupHeadmanUseCase)
    try:
        group = use_case.execute(
            group_uuid=schema.group_uuid,
            new_headman_email=schema.new_headman_email,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )
    return ApiResponse(
        data=GroupSchemaWithHeadman.from_entity(entity=group),
    )


@router.patch(
    '{group_uuid}/add/{lesson_uuid}',
    response=ApiResponse[StatusResponse],
    operation_id='add_lesson_to_group_admin',
    auth=jwt_bearer_admin,
)
def add_lesson_to_group_admin(
        request: HttpRequest,
        group_uuid: str,
        subgroup: Subgroup,
        lesson_uuid: str,
) -> ApiResponse[StatusResponse]:
    container = get_container()
    use_case: AdminAddLessonToGroupUseCase = container.resolve(AdminAddLessonToGroupUseCase)

    try:
        use_case.execute(group_uuid=group_uuid, subgroup=subgroup, lesson_uuid=lesson_uuid)
    except ServiceException as e:
        raise HttpError(
            status_code=404,
            message=e.message,
        )

    return ApiResponse(
        data=StatusResponse(status='Lesson was added successfully'),
    )


@router.patch(
    '{group_uuid}/remove/{lesson_uuid}',
    response=ApiResponse[StatusResponse],
    operation_id='remove_lesson_from_group_admin',
    auth=jwt_bearer_admin,
)
def remove_lesson_from_group_admin(
        request: HttpRequest,
        group_uuid: str,
        subgroup: Subgroup,
        lesson_uuid: str,
) -> ApiResponse[StatusResponse]:
    container = get_container()
    use_case: AdminRemoveLessonFromGroupUseCase = container.resolve(AdminRemoveLessonFromGroupUseCase)

    try:
        use_case.execute(group_uuid=group_uuid, subgroup=subgroup, lesson_uuid=lesson_uuid)
    except ServiceException as e:
        raise HttpError(
            status_code=404,
            message=e.message,
        )

    return ApiResponse(
        data=StatusResponse(status="Lesson was removed successfully"),
    )


@router.patch(
    'add/{lesson_uuid}',
    response=ApiResponse[StatusResponse],
    operation_id='add_lesson_to_group_headman',
    auth=jwt_bearer_headman,
)
def add_lesson_to_group_headman(
        request: HttpRequest,
        subgroup: Subgroup,
        lesson_uuid: str,
) -> ApiResponse[StatusResponse]:
    container = get_container()
    client_service = container.resolve(BaseClientService)
    use_case: HeadmanAddLessonToGroupUseCase = container.resolve(HeadmanAddLessonToGroupUseCase)

    try:
        user_email: str = client_service.get_client_email_from_token(token=request.auth)
    except JWTKeyParsingException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    try:
        use_case.execute(headman_email=user_email, subgroup=subgroup, lesson_uuid=lesson_uuid)
    except ServiceException as e:
        raise HttpError(
            status_code=404,
            message=e.message,
        )

    return ApiResponse(
        data=StatusResponse(status='Lesson was added successfully'),
    )


@router.patch(
    'remove/{lesson_uuid}',
    response=ApiResponse[StatusResponse],
    operation_id='remove_lesson_to_group_headman',
    auth=jwt_bearer_headman,
)
def remove_lesson_to_group_headman(
        request: HttpRequest,
        subgroup: Subgroup,
        lesson_uuid: str,
) -> ApiResponse[StatusResponse]:
    container = get_container()
    client_service = container.resolve(BaseClientService)
    use_case: HeadmanRemoveLessonFromGroupUseCase = container.resolve(HeadmanRemoveLessonFromGroupUseCase)

    try:
        user_email: str = client_service.get_client_email_from_token(token=request.auth)
    except JWTKeyParsingException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    try:
        use_case.execute(headman_email=user_email, subgroup=subgroup, lesson_uuid=lesson_uuid)
    except ServiceException as e:
        raise HttpError(
            status_code=404,
            message=e.message,
        )

    return ApiResponse(
        data=StatusResponse(status="Lesson was removed successfully"),
    )
