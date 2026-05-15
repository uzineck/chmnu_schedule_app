from django.core.cache import cache

import pytest
from tests.factories.client.client import ClientModelFactory
from tests.factories.client.role import RoleModelFactory
from tests.factories.schedule.faculty import FacultyModelFactory
from tests.factories.schedule.group import GroupModelFactory
from tests.factories.schedule.lesson import LessonModelFactory

from core.apps.common.cache.service import (
    BaseCacheService,
    CACHE_MISS,
)
from core.apps.common.models import ClientRole
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.use_cases.group.admin_add_lesson import AdminAddLessonToGroupUseCase
from core.apps.schedule.use_cases.group.create import CreateGroupUseCase
from core.apps.schedule.use_cases.group.get_all import GetAllGroupsUseCase


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def get_all_use_case(container) -> GetAllGroupsUseCase:
    return container.resolve(GetAllGroupsUseCase)


@pytest.fixture
def create_use_case(container) -> CreateGroupUseCase:
    return container.resolve(CreateGroupUseCase)


@pytest.fixture
def cache_service(container) -> BaseCacheService:
    return container.resolve(BaseCacheService)


@pytest.fixture
def group_all_cache_key(cache_service: BaseCacheService) -> str:
    return cache_service.generate_cache_key(model_prefix='group', func_prefix='all')


@pytest.mark.django_db
def test_get_all_caches_on_miss(get_all_use_case, cache_service, group_all_cache_key):
    GroupModelFactory.create_batch(2)
    assert cache_service.get_cache_value(group_all_cache_key, default=CACHE_MISS) is CACHE_MISS

    result = get_all_use_case.execute()

    cached = cache_service.get_cache_value(group_all_cache_key, default=CACHE_MISS)
    assert cached is not CACHE_MISS
    assert len(cached) == 2
    assert cached == result


@pytest.mark.django_db
def test_get_all_returns_cached_value_on_hit(get_all_use_case):
    GroupModelFactory.create(number='ПМ-001')
    first = get_all_use_case.execute()
    assert len(first) == 1

    GroupModelFactory.create(number='ПМ-002')
    second = get_all_use_case.execute()

    assert second == first
    assert len(second) == 1


@pytest.mark.django_db
def test_get_all_caches_empty_result(get_all_use_case, cache_service, group_all_cache_key):
    result = get_all_use_case.execute()
    assert result == []

    cached = cache_service.get_cache_value(group_all_cache_key, default=CACHE_MISS)
    assert cached is not CACHE_MISS
    assert cached == []


@pytest.mark.django_db
def test_create_group_invalidates_get_all_cache(
        get_all_use_case,
        create_use_case,
        cache_service,
        group_all_cache_key,
):
    assert get_all_use_case.execute() == []
    assert cache_service.get_cache_value(group_all_cache_key, default=CACHE_MISS) == []

    faculty = FacultyModelFactory.create()
    headman = ClientModelFactory.create(roles=[RoleModelFactory(id=ClientRole.HEADMAN)])

    create_use_case.execute(
        group_number='ПМ-101',
        faculty_uuid=str(faculty.faculty_uuid),
        headman_email=headman.email,
        has_subgroups=True,
    )

    assert cache_service.get_cache_value(group_all_cache_key, default=CACHE_MISS) is CACHE_MISS

    after = get_all_use_case.execute()
    assert len(after) == 1
    assert after[0].number == 'ПМ-101'


@pytest.mark.django_db
def test_bump_schedule_updated_at_sets_timestamp(container):
    group_service: BaseGroupService = container.resolve(BaseGroupService)
    group = GroupModelFactory.create()
    assert group.schedule_updated_at is None

    group_service.bump_schedule_updated_at(group_id=group.id)

    group.refresh_from_db()
    assert group.schedule_updated_at is not None


@pytest.mark.django_db
def test_admin_add_lesson_bumps_schedule_updated_at(container):
    use_case: AdminAddLessonToGroupUseCase = container.resolve(AdminAddLessonToGroupUseCase)
    group = GroupModelFactory.create(has_subgroups=False)
    lesson = LessonModelFactory.create()

    assert group.schedule_updated_at is None

    use_case.execute(
        group_uuid=str(group.group_uuid),
        subgroup=None,
        lesson_uuid=lesson.lesson_uuid,
    )

    group.refresh_from_db()
    assert group.schedule_updated_at is not None


@pytest.mark.django_db
def test_admin_add_lesson_reflected_in_get_all_after_cache_invalidation(
        get_all_use_case,
        cache_service,
        group_all_cache_key,
        container,
):
    use_case: AdminAddLessonToGroupUseCase = container.resolve(AdminAddLessonToGroupUseCase)
    group = GroupModelFactory.create(has_subgroups=False, number='ПМ-201')
    lesson = LessonModelFactory.create()

    first = get_all_use_case.execute()
    assert len(first) == 1
    assert first[0].schedule_updated_at is None

    use_case.execute(
        group_uuid=str(group.group_uuid),
        subgroup=None,
        lesson_uuid=lesson.lesson_uuid,
    )
    # The use case does not invalidate the cache; the handler does. Simulate handler invalidation:
    cache_service.invalidate_cache_pattern(
        key=cache_service.generate_cache_key(model_prefix='group', func_prefix='all'),
    )

    after = get_all_use_case.execute()
    assert len(after) == 1
    assert after[0].schedule_updated_at is not None
