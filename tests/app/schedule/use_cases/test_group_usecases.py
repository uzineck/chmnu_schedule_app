from django.core.cache import cache

import pytest
from tests.factories.client.client import ClientModelFactory
from tests.factories.client.role import RoleModelFactory
from tests.factories.schedule.group import GroupModelFactory
from tests.factories.schedule.group_lesson import GroupLessonModelFactory
from tests.factories.schedule.lesson import LessonModelFactory

from core.api.filters import PaginationIn
from core.apps.clients.exceptions.client import (
    ClientNotFoundException,
    ClientRoleNotMatchingWithRequiredException,
)
from core.apps.common.filters import SearchFilter
from core.apps.common.models import (
    ClientRole,
    Subgroup,
)
from core.apps.schedule.exceptions.faculty import FacultyNotFoundException
from core.apps.schedule.exceptions.group import (
    GroupAlreadyExistsException,
    GroupHasActiveScheduleException,
    GroupNotFoundException,
    GroupWithoutSubgroupsInvalidSubgroupException,
    HeadmanAssignedToAnotherGroupException,
)
from core.apps.schedule.exceptions.validators.uuid_validator import InvalidUuidFormatStringException
from core.apps.schedule.filters.group import LessonFilter
from core.apps.schedule.use_cases.group.create import CreateGroupUseCase
from core.apps.schedule.use_cases.group.delete import DeleteGroupUseCase
from core.apps.schedule.use_cases.group.get_group_lessons import GetGroupLessonsUseCase
from core.apps.schedule.use_cases.group.get_info import GetGroupInfoUseCase
from core.apps.schedule.use_cases.group.get_list import GetGroupListUseCase
from core.apps.schedule.use_cases.group.update_headman import UpdateGroupHeadmanUseCase


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def create_use_case(container) -> CreateGroupUseCase:
    return container.resolve(CreateGroupUseCase)


@pytest.fixture
def delete_use_case(container) -> DeleteGroupUseCase:
    return container.resolve(DeleteGroupUseCase)


@pytest.fixture
def get_info_use_case(container) -> GetGroupInfoUseCase:
    return container.resolve(GetGroupInfoUseCase)


@pytest.fixture
def get_group_lessons_use_case(container) -> GetGroupLessonsUseCase:
    return container.resolve(GetGroupLessonsUseCase)


@pytest.fixture
def update_headman_use_case(container) -> UpdateGroupHeadmanUseCase:
    return container.resolve(UpdateGroupHeadmanUseCase)


@pytest.fixture
def get_list_use_case(container) -> GetGroupListUseCase:
    return container.resolve(GetGroupListUseCase)


@pytest.fixture
def headman_client():
    def _build(email: str = None):
        role = RoleModelFactory(id=ClientRole.HEADMAN)
        kwargs = {"roles": [role]}
        if email:
            kwargs["email"] = email
        return ClientModelFactory(**kwargs)
    return _build


# --- GetList ---

@pytest.mark.django_db
def test_get_group_list_returns_paginated(get_list_use_case, group_create_batch):
    group_create_batch(size=5)

    items, count = get_list_use_case.execute(
        filters=SearchFilter(),
        pagination_in=PaginationIn(offset=0, limit=10),
    )

    assert count == 5
    assert len(list(items)) == 5


@pytest.mark.django_db
def test_get_group_list_search_filters_by_number(get_list_use_case):
    GroupModelFactory(number="ПМ-101")
    GroupModelFactory(number="ПМ-102")
    GroupModelFactory(number="ІН-201")

    items, count = get_list_use_case.execute(
        filters=SearchFilter(search="ПМ"),
        pagination_in=PaginationIn(offset=0, limit=10),
    )

    items = list(items)
    assert count == 2
    assert {g.number for g in items} == {"ПМ-101", "ПМ-102"}


@pytest.mark.django_db
def test_get_group_list_handles_groups_without_headman(get_list_use_case):
    GroupModelFactory(headman=None)

    items, count = get_list_use_case.execute(
        filters=SearchFilter(),
        pagination_in=PaginationIn(offset=0, limit=10),
    )

    items = list(items)
    assert count == 1
    assert items[0].headman is None


# --- Create ---

@pytest.mark.django_db
def test_create_group_invalid_faculty_uuid_raises(create_use_case, headman_client):
    client = headman_client()

    with pytest.raises(InvalidUuidFormatStringException):
        create_use_case.execute(
            group_number="ПМ-001",
            faculty_uuid="bad",
            headman_email=client.email,
            has_subgroups=True,
        )


@pytest.mark.django_db
def test_create_group_headman_not_found_raises(create_use_case, faculty_create):
    faculty = faculty_create()

    with pytest.raises(ClientNotFoundException):
        create_use_case.execute(
            group_number="ПМ-001",
            faculty_uuid=str(faculty.faculty_uuid),
            headman_email="nobody@gmail.com",
            has_subgroups=True,
        )


@pytest.mark.django_db
def test_create_group_client_lacks_headman_role_raises(create_use_case, faculty_create):
    faculty = faculty_create()
    non_headman = ClientModelFactory(roles=[RoleModelFactory(id=ClientRole.ADMIN)])

    with pytest.raises(ClientRoleNotMatchingWithRequiredException):
        create_use_case.execute(
            group_number="ПМ-001",
            faculty_uuid=str(faculty.faculty_uuid),
            headman_email=non_headman.email,
            has_subgroups=True,
        )


@pytest.mark.django_db
def test_create_group_faculty_not_found_raises(create_use_case, headman_client):
    client = headman_client()

    with pytest.raises(FacultyNotFoundException):
        create_use_case.execute(
            group_number="ПМ-001",
            faculty_uuid="00000000-0000-0000-0000-000000000000",
            headman_email=client.email,
            has_subgroups=True,
        )


@pytest.mark.django_db
def test_create_group_number_already_exists_raises(create_use_case, headman_client, faculty_create):
    GroupModelFactory(number="ПМ-001")
    faculty = faculty_create()
    client = headman_client()

    with pytest.raises(GroupAlreadyExistsException):
        create_use_case.execute(
            group_number="ПМ-001",
            faculty_uuid=str(faculty.faculty_uuid),
            headman_email=client.email,
            has_subgroups=True,
        )


@pytest.mark.django_db
def test_create_group_headman_already_assigned_raises(create_use_case, headman_client, faculty_create):
    faculty = faculty_create()
    client = headman_client()
    GroupModelFactory(headman=client)

    with pytest.raises(HeadmanAssignedToAnotherGroupException):
        create_use_case.execute(
            group_number="ПМ-999",
            faculty_uuid=str(faculty.faculty_uuid),
            headman_email=client.email,
            has_subgroups=True,
        )


@pytest.mark.django_db
def test_create_group_happy_path(create_use_case, headman_client, faculty_create):
    faculty = faculty_create()
    client = headman_client()

    created = create_use_case.execute(
        group_number="ПМ-555",
        faculty_uuid=str(faculty.faculty_uuid),
        headman_email=client.email,
        has_subgroups=False,
    )

    assert created.number == "ПМ-555"
    assert created.headman.id == client.id


# --- Delete ---

@pytest.mark.django_db
def test_delete_group_invalid_uuid_raises(delete_use_case):
    with pytest.raises(InvalidUuidFormatStringException):
        delete_use_case.execute(group_uuid="bad")


@pytest.mark.django_db
def test_delete_group_not_found_raises(delete_use_case):
    with pytest.raises(GroupNotFoundException):
        delete_use_case.execute(group_uuid="00000000-0000-0000-0000-000000000000")


@pytest.mark.django_db
def test_delete_group_has_active_schedule_raises(delete_use_case):
    group = GroupModelFactory()
    lesson = LessonModelFactory()
    GroupLessonModelFactory(group=group, lesson=lesson)

    with pytest.raises(GroupHasActiveScheduleException):
        delete_use_case.execute(group_uuid=str(group.group_uuid))


@pytest.mark.django_db
def test_delete_group_soft_deletes():
    group = GroupModelFactory()
    from core.project.containers.containers import get_container
    use_case = get_container().resolve(DeleteGroupUseCase)

    use_case.execute(group_uuid=str(group.group_uuid))

    group.refresh_from_db()
    assert group.is_active is False


# --- GetInfo ---

@pytest.mark.django_db
def test_get_group_info_invalid_uuid_raises(get_info_use_case):
    with pytest.raises(InvalidUuidFormatStringException):
        get_info_use_case.execute(group_uuid="bad")


@pytest.mark.django_db
def test_get_group_info_happy_path(get_info_use_case):
    group = GroupModelFactory()

    result = get_info_use_case.execute(group_uuid=str(group.group_uuid))

    assert result.uuid == str(group.group_uuid)
    assert result.number == group.number


# --- GetGroupLessons ---

@pytest.mark.django_db
def test_get_group_lessons_invalid_uuid_raises(get_group_lessons_use_case):
    with pytest.raises(InvalidUuidFormatStringException):
        get_group_lessons_use_case.execute(
            group_uuid="bad",
            filters=LessonFilter(is_even=True),
        )


@pytest.mark.django_db
def test_get_group_lessons_subgroup_filter_invalid_for_group_without_subgroups_raises(
        get_group_lessons_use_case,
):
    group = GroupModelFactory(has_subgroups=False)

    with pytest.raises(GroupWithoutSubgroupsInvalidSubgroupException):
        get_group_lessons_use_case.execute(
            group_uuid=str(group.group_uuid),
            filters=LessonFilter(is_even=True, subgroup=Subgroup.A),
        )


@pytest.mark.django_db
def test_get_group_lessons_happy_path(get_group_lessons_use_case):
    group = GroupModelFactory(has_subgroups=False)

    returned_group, views = get_group_lessons_use_case.execute(
        group_uuid=str(group.group_uuid),
        filters=LessonFilter(is_even=True),
    )

    assert returned_group.uuid == str(group.group_uuid)
    assert isinstance(views, list)


# --- UpdateHeadman ---

@pytest.mark.django_db
def test_update_group_headman_invalid_uuid_raises(update_headman_use_case):
    with pytest.raises(InvalidUuidFormatStringException):
        update_headman_use_case.execute(group_uuid="bad", new_headman_email="x@gmail.com")


@pytest.mark.django_db
def test_update_group_headman_group_not_found_raises(update_headman_use_case, headman_client):
    client = headman_client()

    with pytest.raises(GroupNotFoundException):
        update_headman_use_case.execute(
            group_uuid="00000000-0000-0000-0000-000000000000",
            new_headman_email=client.email,
        )


@pytest.mark.django_db
def test_update_group_headman_new_client_not_found_raises(update_headman_use_case):
    group = GroupModelFactory()

    with pytest.raises(ClientNotFoundException):
        update_headman_use_case.execute(
            group_uuid=str(group.group_uuid),
            new_headman_email="ghost@gmail.com",
        )


@pytest.mark.django_db
def test_update_group_headman_new_client_lacks_role_raises(update_headman_use_case):
    group = GroupModelFactory()
    non_headman = ClientModelFactory(roles=[RoleModelFactory(id=ClientRole.ADMIN)])

    with pytest.raises(ClientRoleNotMatchingWithRequiredException):
        update_headman_use_case.execute(
            group_uuid=str(group.group_uuid),
            new_headman_email=non_headman.email,
        )


@pytest.mark.django_db
def test_update_group_headman_happy_path(update_headman_use_case, headman_client):
    group = GroupModelFactory()
    new_headman = headman_client()

    updated, old_email = update_headman_use_case.execute(
        group_uuid=str(group.group_uuid),
        new_headman_email=new_headman.email,
    )

    assert updated.headman.id == new_headman.id
