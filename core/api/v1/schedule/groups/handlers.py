from django.http import HttpRequest
from ninja import (
    Query,
    Router,
)
from ninja.errors import HttpError

from core.api.schemas import (
    ApiResponse,
    StatusResponse,
)
from core.api.v1.schedule.groups.filters import GroupFilter
from core.api.v1.schedule.groups.schemas import (
    CreateGroupSchema,
    GroupLessonsOutSchema,
    GroupSchemaWithHeadman,
    GroupUuidNumberFacultyOutSchema,
    HeadmanEmailInSchema,
)
from core.apps.clients.services.client import BaseClientService
from core.apps.clients.usecases.client.get_headman_info import GetHeadmanInfoUseCase
from core.apps.common.authentication.bearer import (
    jwt_bearer_admin,
    jwt_bearer_headman,
    jwt_bearer_manager,
)
from core.apps.common.cache.service import BaseCacheService
from core.apps.common.cache.timeouts import Timeout
from core.apps.common.exceptions import (
    JWTKeyParsingException,
    ServiceException,
)
from core.apps.common.models import Subgroup
from core.apps.schedule.filters.group import GroupLessonFilter as GroupFilterEntity
from core.apps.schedule.use_cases.group.admin_add_lesson import AdminAddLessonToGroupUseCase
from core.apps.schedule.use_cases.group.admin_remove_lesson import AdminRemoveLessonFromGroupUseCase
from core.apps.schedule.use_cases.group.create import CreateGroupUseCase
from core.apps.schedule.use_cases.group.get_all import GetAllGroupsUseCase
from core.apps.schedule.use_cases.group.get_group_lessons import GetGroupLessonsUseCase
from core.apps.schedule.use_cases.group.get_info import GetGroupInfoUseCase
from core.apps.schedule.use_cases.group.headman_add_lesson import HeadmanAddLessonToGroupUseCase
from core.apps.schedule.use_cases.group.headman_remove_lesson import HeadmanRemoveLessonFromGroupUseCase
from core.apps.schedule.use_cases.group.update_headman import UpdateGroupHeadmanUseCase
from core.project.containers.containers import get_container


router = Router(tags=['Group'])


@router.get(
    'all',
    response=ApiResponse[list[GroupUuidNumberFacultyOutSchema]],
    operation_id='get_all_groups',

)
def get_all_groups(request: HttpRequest) -> ApiResponse[list[GroupUuidNumberFacultyOutSchema]]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: GetAllGroupsUseCase = container.resolve(GetAllGroupsUseCase)
    try:
        groups = use_case.execute()

        cache_key = cache_service.generate_cache_key(model_prefix="group", func_prefix="all")
        items = cache_service.get_cache_value(key=cache_key)
        if not items:
            items = [GroupUuidNumberFacultyOutSchema.from_entity(group) for group in groups]
            cache_service.set_cache(key=cache_key, value=items, timeout=Timeout.MONTH)

    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )
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
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: GetGroupLessonsUseCase = container.resolve(GetGroupLessonsUseCase)
    try:
        cache_key = cache_service.generate_cache_key(
            model_prefix="group",
            identifier=group_uuid,
            func_prefix="lessons",
            filters=filters,
        )
        group_lessons = cache_service.get_cache_value(key=cache_key)
        if not group_lessons:
            group_lessons = use_case.execute(
                group_uuid=group_uuid,
                filters=GroupFilterEntity(subgroup=filters.subgroup, is_even=filters.is_even),
            )
            cache_service.set_cache(key=cache_key, value=group_lessons, timeout=Timeout.DAY)

        group, lessons = group_lessons
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )

    return ApiResponse(
        data=GroupLessonsOutSchema.from_entity_with_lesson_entities(
            group_entity=group,
            lesson_entities=lessons,
            subgroup=filters.subgroup,
        ),
    )


@router.get(
    "{group_uuid}/info",
    response=ApiResponse[GroupSchemaWithHeadman],
    operation_id="get_group_info",
    auth=[jwt_bearer_admin, jwt_bearer_manager],
)
def get_group_info(
        request: HttpRequest,
        group_uuid: str,
) -> ApiResponse[GroupSchemaWithHeadman]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: GetGroupInfoUseCase = container.resolve(GetGroupInfoUseCase)
    try:
        cache_key = cache_service.generate_cache_key(
            model_prefix="group",
            identifier=group_uuid,
            func_prefix="info",
        )
        group = cache_service.get_cache_value(key=cache_key)
        if not group:
            group = use_case.execute(group_uuid=group_uuid)
            cache_service.set_cache(key=cache_key, value=group, timeout=Timeout.WEEK)

    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )

    return ApiResponse(
        data=GroupSchemaWithHeadman.from_entity(group),
    )


@router.get(
    "{headman_email}/headman_info",
    response=ApiResponse[GroupSchemaWithHeadman],
    operation_id='get_headman_info',
    auth=[jwt_bearer_admin, jwt_bearer_manager],
)
def get_headman_info(
        request: HttpRequest,
        headman_email: str,
) -> ApiResponse[GroupSchemaWithHeadman]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: GetHeadmanInfoUseCase = container.resolve(GetHeadmanInfoUseCase)
    try:
        cache_key = cache_service.generate_cache_key(
            model_prefix="group",
            identifier=headman_email,
            func_prefix="info",
        )
        group_headman = cache_service.get_cache_value(key=cache_key)
        if not group_headman:
            group_headman = use_case.execute(
                email=headman_email,
            )
            cache_service.set_cache(key=cache_key, value=group_headman, timeout=Timeout.WEEK)

        group, headman = group_headman

    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )

    return ApiResponse(
        data=GroupSchemaWithHeadman.from_entity(entity=group),
    )


@router.post(
    '',
    response={201: ApiResponse[GroupSchemaWithHeadman]},
    operation_id='create_group',
    auth=[jwt_bearer_admin, jwt_bearer_manager],
)
def create_group(request: HttpRequest, schema: CreateGroupSchema) -> ApiResponse[GroupSchemaWithHeadman]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: CreateGroupUseCase = container.resolve(CreateGroupUseCase)
    try:
        group = use_case.execute(
            group_number=schema.number,
            faculty_uuid=schema.faculty_uuid,
            headman_email=schema.headman_email,
            has_subgroups=schema.has_subgroups,
        )
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="group",
                    func_prefix="all",
                ),
            ],
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
    "{group_uuid}/update_headman",
    response=ApiResponse[GroupSchemaWithHeadman],
    operation_id='update_group_headman',
    auth=[jwt_bearer_admin, jwt_bearer_manager],
)
def update_group_headman(
        request: HttpRequest,
        group_uuid: str,
        schema: HeadmanEmailInSchema,
) -> ApiResponse[GroupSchemaWithHeadman]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: UpdateGroupHeadmanUseCase = container.resolve(UpdateGroupHeadmanUseCase)
    try:
        group = use_case.execute(
            group_uuid=group_uuid,
            new_headman_email=schema.headman_email,
        )
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="group",
                    identifier="*",
                    func_prefix="info",
                ),
            ],
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
    auth=[jwt_bearer_admin, jwt_bearer_manager],
)
def add_lesson_to_group_admin(
        request: HttpRequest,
        group_uuid: str,
        subgroup: Subgroup,
        lesson_uuid: str,
) -> ApiResponse[StatusResponse]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: AdminAddLessonToGroupUseCase = container.resolve(AdminAddLessonToGroupUseCase)
    try:
        group, lesson = use_case.execute(group_uuid=group_uuid, subgroup=subgroup, lesson_uuid=lesson_uuid)
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="group",
                    identifier=group.uuid,
                    func_prefix="lessons",
                    filters="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="teacher",
                    identifier=lesson.teacher.uuid,
                    func_prefix="lessons",
                ),
            ],
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )

    return ApiResponse(
        data=StatusResponse(status='Lesson was added successfully'),
    )


@router.patch(
    '{group_uuid}/remove/{lesson_uuid}',
    response=ApiResponse[StatusResponse],
    operation_id='remove_lesson_from_group_admin',
    auth=[jwt_bearer_admin, jwt_bearer_manager],
)
def remove_lesson_from_group_admin(
        request: HttpRequest,
        group_uuid: str,
        subgroup: Subgroup,
        lesson_uuid: str,
) -> ApiResponse[StatusResponse]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: AdminRemoveLessonFromGroupUseCase = container.resolve(AdminRemoveLessonFromGroupUseCase)
    try:
        group, lesson = use_case.execute(group_uuid=group_uuid, subgroup=subgroup, lesson_uuid=lesson_uuid)
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="group",
                    identifier=group.uuid,
                    func_prefix="lessons",
                    filters="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="teacher",
                    identifier=lesson.teacher.uuid,
                    func_prefix="lessons",
                ),
            ],
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
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
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: HeadmanAddLessonToGroupUseCase = container.resolve(HeadmanAddLessonToGroupUseCase)

    try:
        user_email: str = client_service.get_client_email_from_token(token=request.auth)
        group, lesson = use_case.execute(headman_email=user_email, subgroup=subgroup, lesson_uuid=lesson_uuid)
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="group",
                    identifier=group.uuid,
                    func_prefix="lessons",
                    filters="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="teacher",
                    identifier=lesson.teacher.uuid,
                    func_prefix="lessons",
                ),
            ],
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
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
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: HeadmanRemoveLessonFromGroupUseCase = container.resolve(HeadmanRemoveLessonFromGroupUseCase)

    try:
        user_email: str = client_service.get_client_email_from_token(token=request.auth)
        group, lesson = use_case.execute(headman_email=user_email, subgroup=subgroup, lesson_uuid=lesson_uuid)
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="group",
                    identifier=group.uuid,
                    func_prefix="lessons",
                    filters="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="teacher",
                    identifier=lesson.teacher.uuid,
                    func_prefix="lessons",
                ),
            ],
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )

    return ApiResponse(
        data=StatusResponse(status="Lesson was removed successfully"),
    )
