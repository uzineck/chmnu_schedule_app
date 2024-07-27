from django.http import HttpRequest
from ninja import (
    Query,
    Router,
)
from ninja.errors import HttpError
from ninja.security import django_auth_superuser

from core.api.schemas import ApiResponse
from core.api.v1.schedule.groups.filters import GroupFilter
from core.api.v1.schedule.groups.schemas import (
    CreateGroupSchema,
    GroupLessonsOutSchema,
    GroupSchema,
    UpdateGroupHeadmanSchema,
)
from core.api.v1.schedule.lessons.schema_for_groups import LessonForGroupOutSchema
from core.apps.common.authentication.bearer import jwt_bearer
from core.apps.common.exceptions import ServiceException
from core.apps.schedule.filters.group import GroupFilter as GroupFilterEntity
from core.apps.schedule.services.groups import BaseGroupService
from core.apps.schedule.use_cases.group.create_group import CreateGroupUseCase
from core.apps.schedule.use_cases.group.get_group_lessons import GetGroupLessonsUseCase
from core.apps.schedule.use_cases.group.update_headman import UpdateGroupHeadmanUseCase
from core.project.containers import get_container


router = Router(tags=['Group'])


@router.get(
    "lessons",
    response=ApiResponse[GroupLessonsOutSchema],
    operation_id="get_group_lessons",
)
def get_group_lessons(
        request: HttpRequest,
        group_number: str,
        filters: Query[GroupFilter],
) -> ApiResponse[GroupLessonsOutSchema]:
    container = get_container()
    use_case: GetGroupLessonsUseCase = container.resolve(GetGroupLessonsUseCase)
    try:
        group, lessons = use_case.execute(
            group_number=group_number,
            filters=GroupFilterEntity(
                subgroup=filters.subgroup,
                is_even=filters.is_even,
            ),
        )
        items = [LessonForGroupOutSchema.from_entity(obj) for obj in lessons]

    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=GroupLessonsOutSchema(
            number=group.number,
            headman=group.headman,
            has_subgroups=group.has_subgroups,
            lessons=items,
        ),
    )


@router.get(
    "info",
    response=ApiResponse[GroupSchema],
    operation_id="get_group_info",
    auth=django_auth_superuser,
)
def get_group_info(
        request: HttpRequest,
        group_number: str,
) -> ApiResponse[GroupSchema]:
    container = get_container()
    service: BaseGroupService = container.resolve(BaseGroupService)
    try:
        group = service.get_group_by_number(group_number=group_number)

    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=GroupSchema(
            number=group.number,
            headman=group.headman,
            has_subgroups=group.has_subgroups,
        ),
    )


@router.post('', response=ApiResponse[GroupSchema], operation_id='create_group', auth=django_auth_superuser)
def get_or_create_group(request: HttpRequest, schema: CreateGroupSchema) -> ApiResponse[GroupSchema]:
    container = get_container()
    use_case: CreateGroupUseCase = container.resolve(CreateGroupUseCase)
    try:
        group = use_case.execute(
            group_number=schema.number,
            headman_email=schema.headman_email,
            has_subgroups=schema.has_subgroups,
        )

    except ServiceException as e:
        raise HttpError(
            status_code=404,
            message=e.message,
        )

    return ApiResponse(
        data=GroupSchema(
            number=group.number,
            headman=group.headman,
            has_subgroups=group.has_subgroups,
        ),
    )


@router.patch(
    "update_group_headman",
    response=ApiResponse[GroupSchema],
    operation_id='update_group_headman',
    auth=django_auth_superuser,
)
def update_group_headman(request: HttpRequest, schema: UpdateGroupHeadmanSchema) -> ApiResponse[GroupSchema]:
    container = get_container()
    use_case: UpdateGroupHeadmanUseCase = container.resolve(UpdateGroupHeadmanUseCase)
    try:
        group = use_case.execute(
            group_number=schema.group_number,
            headman_email=schema.headman_email,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )
    return ApiResponse(
        data=GroupSchema(
            number=group.number,
            headman=group.headman,
            has_subgroups=group.has_subgroups,
        ),
    )


@router.patch(
    '{group_number}/add/{lesson_id}',
    response=ApiResponse[GroupSchema],
    operation_id='add_lesson_to_group',
    auth=jwt_bearer,
)
def add_lesson_to_group(request: HttpRequest, group_number: str, lesson_id: int) -> ApiResponse[GroupSchema]:
    container = get_container()
    service: BaseGroupService = container.resolve(BaseGroupService)
    try:
        group = service.add_lesson(group_number=group_number, lesson_id=lesson_id)

    except ServiceException as e:
        raise HttpError(
            status_code=404,
            message=e.message,
        )

    return ApiResponse(
        data=GroupSchema(
            number=group.number,
            headman=group.headman,
            has_subgroups=group.has_subgroups,
            lessons=group.lessons,
        ),
    )


@router.patch(
    '{group_number}/remove/{lesson_id}',
    response=ApiResponse[GroupSchema],
    operation_id='remove_lesson_from_group',
    auth=jwt_bearer,
)
def remove_lesson_from_group(request: HttpRequest, group_number: str, lesson_id: int) -> ApiResponse[GroupSchema]:
    container = get_container()
    service: BaseGroupService = container.resolve(BaseGroupService)
    try:
        group = service.remove_lesson(group_number=group_number, lesson_id=lesson_id)

    except ServiceException as e:
        raise HttpError(
            status_code=404,
            message=e.message,
        )

    return ApiResponse(
        data=GroupSchema(
            number=group.number,
            headman=group.headman,
            has_subgroups=group.has_subgroups,
            lessons=group.lessons,
        ),
    )
