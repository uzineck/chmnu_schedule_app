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
from core.apps.common.filters import SearchFilter as SearchFilterEntity
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
from core.apps.schedule.use_cases.group.get_list import GetGroupListUseCase
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
    summary="List every active group (public)",
    description=(
        "Returns every active group with its faculty, subgroup flag, and the timestamp of the "
        "group's last schedule edit (`schedule_updated_at`). This endpoint is public — clients use "
        "it to populate the group picker before login."
    ),
)
def get_all_groups(request: HttpRequest) -> ApiResponse[list[GroupAllOutSchema]]:
    container = get_container()
    use_case: GetAllGroupsUseCase = container.resolve(GetAllGroupsUseCase)
    items = [GroupAllOutSchema.from_entity(obj) for obj in use_case.execute()]
    return ApiResponse(
        data=items,
    )


@router.get(
    "",
    response={
        200: ApiResponse[ListPaginatedResponse[GroupSchemaWithHeadman]],
        401: ApiErrorResponse,
        403: ApiErrorResponse,
    },
    operation_id="get_group_list",
    auth=jwt_auth_group_manager,
    summary="Search and paginate groups",
    description=(
        "Returns a paginated list of active groups with their faculty and headman. The `search` "
        "query parameter performs a case-insensitive match against the group number. Requires "
        "ADMIN or GROUP_MANAGER role."
    ),
)
def get_group_list(
        request: HttpRequest,
        filters: Query[SearchFilter],
        pagination_in: Query[PaginationIn],
) -> ApiResponse[ListPaginatedResponse[GroupSchemaWithHeadman]]:
    container = get_container()
    use_case: GetGroupListUseCase = container.resolve(GetGroupListUseCase)
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
            items=[GroupSchemaWithHeadman.from_entity(obj) for obj in item_list],
            pagination=pagination_out,
        ),
    )


@router.get(
    "{group_uuid}/lessons",
    response={
        200: ApiResponse[GroupLessonsOutSchema],
        404: ApiErrorResponse,
    },
    operation_id="get_group_lessons",
    summary="Get a group's schedule (public)",
    description=(
        "Returns the lessons assigned to the given group for the requested week parity "
        "(`is_even=true` for even weeks, `false` for odd). If the group uses subgroups, pass "
        "`subgroup=A` or `subgroup=B` to filter to that subgroup; omit it to get every lesson "
        "regardless of subgroup. Public — no authentication required."
    ),
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
    response={
        200: ApiResponse[GroupSchemaWithHeadman],
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
    },
    operation_id="get_group_info",
    auth=jwt_auth_group_manager,
    summary="Admin: get a group's metadata",
    description=(
        "Returns the group's identity, faculty, subgroup flag, and current headman. Requires "
        "ADMIN or GROUP_MANAGER role."
    ),
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
    response={
        200: ApiResponse[GroupSchema],
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
    },
    operation_id='get_headman_group',
    auth=jwt_auth_headman,
    summary="Headman: get my group",
    description=(
        "Returns the group that the authenticated headman owns. Requires HEADMAN role; returns 404 "
        "if the caller is not currently registered as a headman of any active group."
    ),
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
    response={
        201: ApiResponse[GroupSchemaWithHeadman],
        400: ApiErrorResponse,
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
        409: ApiErrorResponse,
    },
    operation_id='create_group',
    auth=jwt_auth_group_manager,
    summary="Create a group",
    description=(
        "Registers a new group under a faculty and assigns its headman (by email). The headman "
        "client must already exist. Returns 409 if the group number already exists in the faculty, "
        "or 404 if the faculty or headman cannot be found."
    ),
)
def create_group(
        request: HttpRequest,
        schema: CreateGroupSchema,
) -> tuple[int, ApiResponse[GroupSchemaWithHeadman]]:
    container = get_container()
    use_case: CreateGroupUseCase = container.resolve(CreateGroupUseCase)
    group = use_case.execute(
        group_number=schema.number,
        faculty_uuid=schema.faculty_uuid,
        headman_email=schema.headman_email,
        has_subgroups=schema.has_subgroups,
    )

    return 201, ApiResponse(
        data=GroupSchemaWithHeadman.from_entity(entity=group),
    )


@router.delete(
    "{group_uuid}",
    response={
        200: ApiResponse[StatusResponse],
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
    },
    operation_id='delete_group',
    auth=jwt_auth_group_manager,
    summary="Soft-delete a group",
    description="Marks the group inactive and removes its lesson assignments.",
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
    response={
        200: ApiResponse[GroupSchemaWithHeadman],
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
    },
    operation_id='update_group_headman',
    auth=jwt_auth_group_manager,
    summary="Replace a group's headman",
    description=(
        "Reassigns the group's headman to the client identified by `headman_email`. The previous "
        "headman loses the HEADMAN role for this group."
    ),
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
    response={
        200: ApiResponse[StatusResponse],
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
        409: ApiErrorResponse,
    },
    operation_id='add_lesson_to_group_admin',
    auth=jwt_auth_schedule_manager,
    summary="Admin: attach a lesson to a group",
    description=(
        "Adds an existing lesson to the target group. Optional `subgroup` query parameter scopes "
        "the assignment to a single subgroup (A or B); omit it to assign to the whole group. "
        "Returns 409 if the lesson is already attached or conflicts with an existing timeslot. "
        "Requires ADMIN or SCHEDULE_MANAGER role."
    ),
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
    response={
        200: ApiResponse[StatusResponse],
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
        409: ApiErrorResponse,
    },
    operation_id='update_lesson_in_group_admin',
    auth=jwt_auth_schedule_manager,
    summary="Admin: replace one of a group's lessons",
    description=(
        "Swaps `old_lesson_uuid` for `lesson_uuid` within the target group (and optional "
        "subgroup), preserving the assignment in a single operation. Requires ADMIN or "
        "SCHEDULE_MANAGER role."
    ),
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
    response={
        200: ApiResponse[StatusResponse],
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
    },
    operation_id='remove_lesson_from_group_admin',
    auth=jwt_auth_schedule_manager,
    summary="Admin: detach a lesson from a group",
    description=(
        "Removes the lesson assignment from the group. With `subgroup` supplied, removes only the "
        "subgroup-scoped assignment. Requires ADMIN or SCHEDULE_MANAGER role."
    ),
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
    response={
        200: ApiResponse[StatusResponse],
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
        409: ApiErrorResponse,
    },
    operation_id='add_lesson_to_group_headman',
    auth=jwt_auth_headman,
    summary="Headman: attach a lesson to my group",
    description=(
        "Headman-scoped version of the admin add-lesson endpoint. The target group is inferred "
        "from the authenticated headman; the caller cannot affect any other group. Requires "
        "HEADMAN role."
    ),
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
    response={
        200: ApiResponse[StatusResponse],
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
        409: ApiErrorResponse,
    },
    operation_id='update_lesson_in_group_headman',
    auth=jwt_auth_headman,
    summary="Headman: replace one of my group's lessons",
    description=(
        "Headman-scoped lesson swap, targeting the caller's group only. Requires HEADMAN role."
    ),
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
    response={
        200: ApiResponse[StatusResponse],
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
    },
    operation_id='remove_lesson_from_group_headman',
    auth=jwt_auth_headman,
    summary="Headman: detach a lesson from my group",
    description=(
        "Headman-scoped lesson removal, targeting the caller's group only. Requires HEADMAN role."
    ),
)
def remove_lesson_from_group_headman(
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
