from django.http import HttpRequest
from ninja import (
    Query,
    Router,
)

from core.api.schemas import (
    ApiResponse,
    StatusResponse,
)
from core.api.v1.schedule.groups.filters import GroupLessonFilter
from core.api.v1.schedule.groups.schemas import (
    CreateGroupSchema,
    GroupAllOutSchema,
    GroupLessonsOutSchema,
    GroupSchema,
    GroupSchemaWithHeadman,
    HeadmanEmailInSchema,
)
from core.apps.clients.usecases.headman.get_headman_group import GetHeadmanGroupUseCase
from core.apps.common.authentication.ninja_auth import (
    jwt_auth_group_manager,
    jwt_auth_headman,
    jwt_auth_schedule_manager,
)
from core.apps.common.models import Subgroup
from core.apps.schedule.filters.group import LessonFilter
from core.apps.schedule.use_cases.group.admin_add_lesson import AdminAddLessonToGroupUseCase
from core.apps.schedule.use_cases.group.admin_remove_lesson import AdminRemoveLessonFromGroupUseCase
from core.apps.schedule.use_cases.group.admin_update_lesson import AdminUpdateLessonInGroupUseCase
from core.apps.schedule.use_cases.group.create import CreateGroupUseCase
from core.apps.schedule.use_cases.group.delete import DeleteGroupUseCase
from core.apps.schedule.use_cases.group.get_all import GetAllGroupsUseCase
from core.apps.schedule.use_cases.group.get_group_lessons import GetGroupLessonsUseCase
from core.apps.schedule.use_cases.group.get_info import GetGroupInfoUseCase
from core.apps.schedule.use_cases.group.headman_add_lesson import HeadmanAddLessonToGroupUseCase
from core.apps.schedule.use_cases.group.headman_remove_lesson import HeadmanRemoveLessonFromGroupUseCase
from core.apps.schedule.use_cases.group.headman_update_lesson import HeadmanUpdateLessonInGroupUseCase
from core.apps.schedule.use_cases.group.update_headman import UpdateGroupHeadmanUseCase
from core.project.containers.containers import get_container


router = Router(tags=['Group'])


@router.get(
    'all',
    response=ApiResponse[list[GroupAllOutSchema]],
    operation_id='get_all_groups',

)
def get_all_groups(request: HttpRequest) -> ApiResponse[list[GroupAllOutSchema]]:
    container = get_container()
    use_case: GetAllGroupsUseCase = container.resolve(GetAllGroupsUseCase)
    items = [GroupAllOutSchema.from_entity(obj) for obj in use_case.execute()]
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
        filters: Query[GroupLessonFilter],
) -> ApiResponse[GroupLessonsOutSchema]:
    container = get_container()
    use_case: GetGroupLessonsUseCase = container.resolve(GetGroupLessonsUseCase)

    group, views = use_case.execute(
        group_uuid=group_uuid,
        filters=LessonFilter(subgroup=filters.subgroup, is_even=filters.is_even),
    )

    return ApiResponse(
        data=GroupLessonsOutSchema.from_views(
            group_entity=group,
            lesson_views=views,
            subgroup=filters.subgroup,
        ),
    )


@router.get(
    "{group_uuid}/info",
    response=ApiResponse[GroupSchemaWithHeadman],
    operation_id="get_group_info",
    auth=jwt_auth_group_manager,
)
def get_group_info(
        request: HttpRequest,
        group_uuid: str,
) -> ApiResponse[GroupSchemaWithHeadman]:
    container = get_container()
    use_case: GetGroupInfoUseCase = container.resolve(GetGroupInfoUseCase)
    item = use_case.execute(group_uuid=group_uuid)

    return ApiResponse(
        data=GroupSchemaWithHeadman.from_entity(item),
    )


@router.get(
    "headman_group",
    response=ApiResponse[GroupSchema],
    operation_id='get_headman_group',
    auth=jwt_auth_headman,
)
def get_headman_group(
        request: HttpRequest,
) -> ApiResponse[GroupSchema]:
    container = get_container()
    use_case: GetHeadmanGroupUseCase = container.resolve(GetHeadmanGroupUseCase)
    item = use_case.execute(email=request.client_email)

    return ApiResponse(
        data=GroupSchema.from_entity(entity=item),
    )


@router.post(
    '',
    response={201: ApiResponse[GroupSchemaWithHeadman]},
    operation_id='create_group',
    auth=jwt_auth_group_manager,
)
def create_group(request: HttpRequest, schema: CreateGroupSchema) -> ApiResponse[GroupSchemaWithHeadman]:
    container = get_container()
    use_case: CreateGroupUseCase = container.resolve(CreateGroupUseCase)
    group = use_case.execute(
        group_number=schema.number,
        faculty_uuid=schema.faculty_uuid,
        headman_email=schema.headman_email,
        has_subgroups=schema.has_subgroups,
    )

    return ApiResponse(
        data=GroupSchemaWithHeadman.from_entity(entity=group),
    )


@router.delete(
    "{group_uuid}",
    response=ApiResponse[StatusResponse],
    operation_id='delete_group',
    auth=jwt_auth_group_manager,
)
def delete_group(request: HttpRequest, group_uuid: str) -> ApiResponse[StatusResponse]:
    container = get_container()
    use_case: DeleteGroupUseCase = container.resolve(DeleteGroupUseCase)
    use_case.execute(group_uuid=group_uuid)

    return ApiResponse(
        data=StatusResponse(status="Group deleted successfully"),
    )


@router.patch(
    "{group_uuid}/update_headman",
    response=ApiResponse[GroupSchemaWithHeadman],
    operation_id='update_group_headman',
    auth=jwt_auth_group_manager,
)
def update_group_headman(
        request: HttpRequest,
        group_uuid: str,
        schema: HeadmanEmailInSchema,
) -> ApiResponse[GroupSchemaWithHeadman]:
    container = get_container()
    use_case: UpdateGroupHeadmanUseCase = container.resolve(UpdateGroupHeadmanUseCase)
    group, _ = use_case.execute(
        group_uuid=group_uuid,
        new_headman_email=schema.headman_email,
    )
    return ApiResponse(
        data=GroupSchemaWithHeadman.from_entity(entity=group),
    )


@router.patch(
    '{group_uuid}/add/{lesson_uuid}',
    response=ApiResponse[StatusResponse],
    operation_id='add_lesson_to_group_admin',
    auth=jwt_auth_schedule_manager,
)
def add_lesson_to_group_admin(
        request: HttpRequest,
        group_uuid: str,
        lesson_uuid: str,
        subgroup: Subgroup | None = None,
) -> ApiResponse[StatusResponse]:
    container = get_container()
    use_case: AdminAddLessonToGroupUseCase = container.resolve(AdminAddLessonToGroupUseCase)
    use_case.execute(group_uuid=group_uuid, subgroup=subgroup, lesson_uuid=lesson_uuid)

    return ApiResponse(
        data=StatusResponse(status='Lesson was added successfully'),
    )


@router.patch(
    '{group_uuid}/{old_lesson_uuid}/update/{lesson_uuid}',
    response=ApiResponse[StatusResponse],
    operation_id='update_lesson_in_group_admin',
    auth=jwt_auth_schedule_manager,
)
def update_lesson_in_group_admin(
        request: HttpRequest,
        group_uuid: str,
        lesson_uuid: str,
        old_lesson_uuid: str,
        subgroup: Subgroup | None = None,
) -> ApiResponse[StatusResponse]:
    container = get_container()
    use_case: AdminUpdateLessonInGroupUseCase = container.resolve(AdminUpdateLessonInGroupUseCase)
    use_case.execute(
        group_uuid=group_uuid,
        subgroup=subgroup,
        lesson_uuid=lesson_uuid,
        old_lesson_uuid=old_lesson_uuid,
    )

    return ApiResponse(
        data=StatusResponse(status='Lesson was updated successfully'),
    )


@router.patch(
    '{group_uuid}/remove/{lesson_uuid}',
    response=ApiResponse[StatusResponse],
    operation_id='remove_lesson_from_group_admin',
    auth=jwt_auth_schedule_manager,
)
def remove_lesson_from_group_admin(
        request: HttpRequest,
        group_uuid: str,
        lesson_uuid: str,
        subgroup: Subgroup | None = None,
) -> ApiResponse[StatusResponse]:
    container = get_container()
    use_case: AdminRemoveLessonFromGroupUseCase = container.resolve(AdminRemoveLessonFromGroupUseCase)
    use_case.execute(group_uuid=group_uuid, subgroup=subgroup, lesson_uuid=lesson_uuid)
    return ApiResponse(
        data=StatusResponse(status="Lesson was removed successfully"),
    )


@router.patch(
    'add/{lesson_uuid}',
    response=ApiResponse[StatusResponse],
    operation_id='add_lesson_to_group_headman',
    auth=jwt_auth_headman,
)
def add_lesson_to_group_headman(
        request: HttpRequest,
        lesson_uuid: str,
        subgroup: Subgroup | None = None,
) -> ApiResponse[StatusResponse]:
    container = get_container()
    use_case: HeadmanAddLessonToGroupUseCase = container.resolve(HeadmanAddLessonToGroupUseCase)
    use_case.execute(headman_email=request.client_email, subgroup=subgroup, lesson_uuid=lesson_uuid)

    return ApiResponse(
        data=StatusResponse(status='Lesson was added successfully'),
    )


@router.patch(
    '{old_lesson_uuid}/update/{lesson_uuid}',
    response=ApiResponse[StatusResponse],
    operation_id='update_lesson_in_group_headman',
    auth=jwt_auth_headman,
)
def update_lesson_in_group_headman(
        request: HttpRequest,
        lesson_uuid: str,
        old_lesson_uuid: str,
        subgroup: Subgroup | None = None,
) -> ApiResponse[StatusResponse]:
    container = get_container()
    use_case: HeadmanUpdateLessonInGroupUseCase = container.resolve(HeadmanUpdateLessonInGroupUseCase)
    use_case.execute(
        headman_email=request.client_email,
        subgroup=subgroup,
        lesson_uuid=lesson_uuid,
        old_lesson_uuid=old_lesson_uuid,
    )

    return ApiResponse(
        data=StatusResponse(status='Lesson was updated successfully'),
    )


@router.patch(
    'remove/{lesson_uuid}',
    response=ApiResponse[StatusResponse],
    operation_id='remove_lesson_to_group_headman',
    auth=jwt_auth_headman,
)
def remove_lesson_to_group_headman(
        request: HttpRequest,
        lesson_uuid: str,
        subgroup: Subgroup | None = None,
) -> ApiResponse[StatusResponse]:
    container = get_container()
    use_case: HeadmanRemoveLessonFromGroupUseCase = container.resolve(HeadmanRemoveLessonFromGroupUseCase)
    use_case.execute(headman_email=request.client_email, subgroup=subgroup, lesson_uuid=lesson_uuid)

    return ApiResponse(
        data=StatusResponse(status="Lesson was removed successfully"),
    )
