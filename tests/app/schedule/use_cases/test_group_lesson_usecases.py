from django.core.cache import cache

import pytest
from tests.factories.client.client import ClientModelFactory
from tests.factories.client.role import RoleModelFactory
from tests.factories.schedule.group import GroupModelFactory
from tests.factories.schedule.group_lesson import GroupLessonModelFactory
from tests.factories.schedule.lesson import LessonModelFactory

from core.apps.clients.exceptions.client import (
    ClientNotFoundException,
    ClientRoleNotMatchingWithRequiredException,
)
from core.apps.common.models import (
    ClientRole,
    Subgroup,
)
from core.apps.schedule.exceptions.group import (
    GroupNotFoundException,
    GroupWithoutSubgroupsInvalidSubgroupException,
    HeadmanNotAssignedToAnyGroup,
)
from core.apps.schedule.exceptions.group_lesson import (
    GroupLessonAlreadyExists,
    GroupLessonDeleteError,
)
from core.apps.schedule.exceptions.lesson import LessonNotFoundException
from core.apps.schedule.exceptions.validators.uuid_validator import InvalidUuidFormatStringException
from core.apps.schedule.models import (
    GroupLesson as GroupLessonModel,
    Lesson as LessonModel,
)
from core.apps.schedule.use_cases.group.admin_remove_lesson import AdminRemoveLessonFromGroupUseCase
from core.apps.schedule.use_cases.group.admin_update_lesson import AdminUpdateLessonInGroupUseCase
from core.apps.schedule.use_cases.group.headman_add_lesson import HeadmanAddLessonToGroupUseCase
from core.apps.schedule.use_cases.group.headman_remove_lesson import HeadmanRemoveLessonFromGroupUseCase
from core.apps.schedule.use_cases.group.headman_update_lesson import HeadmanUpdateLessonInGroupUseCase


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def headman_client():
    role = RoleModelFactory(id=ClientRole.HEADMAN)
    return ClientModelFactory(roles=[role])


@pytest.fixture
def admin_remove_use_case(container) -> AdminRemoveLessonFromGroupUseCase:
    return container.resolve(AdminRemoveLessonFromGroupUseCase)


@pytest.fixture
def admin_update_use_case(container) -> AdminUpdateLessonInGroupUseCase:
    return container.resolve(AdminUpdateLessonInGroupUseCase)


@pytest.fixture
def headman_add_use_case(container) -> HeadmanAddLessonToGroupUseCase:
    return container.resolve(HeadmanAddLessonToGroupUseCase)


@pytest.fixture
def headman_remove_use_case(container) -> HeadmanRemoveLessonFromGroupUseCase:
    return container.resolve(HeadmanRemoveLessonFromGroupUseCase)


@pytest.fixture
def headman_update_use_case(container) -> HeadmanUpdateLessonInGroupUseCase:
    return container.resolve(HeadmanUpdateLessonInGroupUseCase)


@pytest.mark.django_db
def test_admin_remove_invalid_uuid_raises(admin_remove_use_case):
    with pytest.raises(InvalidUuidFormatStringException):
        admin_remove_use_case.execute(group_uuid="bad", subgroup=None, lesson_uuid="bad")


@pytest.mark.django_db
def test_admin_remove_group_not_found_raises(admin_remove_use_case):
    with pytest.raises(GroupNotFoundException):
        admin_remove_use_case.execute(
            group_uuid="00000000-0000-0000-0000-000000000000",
            subgroup=None,
            lesson_uuid="00000000-0000-0000-0000-000000000001",
        )


@pytest.mark.django_db
def test_admin_remove_missing_group_lesson_raises(admin_remove_use_case):
    group = GroupModelFactory(has_subgroups=False)
    lesson = LessonModelFactory()

    with pytest.raises(GroupLessonDeleteError):
        admin_remove_use_case.execute(
            group_uuid=str(group.group_uuid),
            subgroup=None,
            lesson_uuid=str(lesson.lesson_uuid),
        )


@pytest.mark.django_db
def test_admin_remove_happy_path_orphan_lesson_deleted(admin_remove_use_case):
    group = GroupModelFactory(has_subgroups=False)
    lesson = LessonModelFactory()
    GroupLessonModelFactory(group=group, lesson=lesson, subgroup=None)

    returned_group, returned_lesson = admin_remove_use_case.execute(
        group_uuid=str(group.group_uuid),
        subgroup=None,
        lesson_uuid=str(lesson.lesson_uuid),
    )

    assert returned_group.uuid == str(group.group_uuid)
    assert returned_lesson.uuid == str(lesson.lesson_uuid)
    assert not LessonModel.objects.filter(pk=lesson.pk).exists()


@pytest.mark.django_db
def test_admin_remove_happy_path_lesson_still_attached_elsewhere_not_deleted(admin_remove_use_case):
    group_a = GroupModelFactory(has_subgroups=False)
    group_b = GroupModelFactory(has_subgroups=False)
    lesson = LessonModelFactory()
    GroupLessonModelFactory(group=group_a, lesson=lesson, subgroup=None)
    GroupLessonModelFactory(group=group_b, lesson=lesson, subgroup=None)

    admin_remove_use_case.execute(
        group_uuid=str(group_a.group_uuid),
        subgroup=None,
        lesson_uuid=str(lesson.lesson_uuid),
    )

    assert LessonModel.objects.filter(pk=lesson.pk).exists()


@pytest.mark.django_db
def test_admin_update_invalid_uuid_raises(admin_update_use_case):
    with pytest.raises(InvalidUuidFormatStringException):
        admin_update_use_case.execute(
            group_uuid="bad",
            subgroup=None,
            lesson_uuid="bad",
            old_lesson_uuid="bad",
        )


@pytest.mark.django_db
def test_admin_update_old_lesson_not_found_raises(admin_update_use_case):
    group = GroupModelFactory(has_subgroups=False)

    with pytest.raises(LessonNotFoundException):
        admin_update_use_case.execute(
            group_uuid=str(group.group_uuid),
            subgroup=None,
            lesson_uuid="00000000-0000-0000-0000-000000000001",
            old_lesson_uuid="00000000-0000-0000-0000-000000000002",
        )


@pytest.mark.django_db
def test_admin_update_new_lesson_already_in_group_raises(admin_update_use_case):
    group = GroupModelFactory(has_subgroups=False)
    old_lesson = LessonModelFactory()
    new_lesson = LessonModelFactory()
    GroupLessonModelFactory(group=group, lesson=old_lesson, subgroup=None)
    GroupLessonModelFactory(group=group, lesson=new_lesson, subgroup=None)

    with pytest.raises(GroupLessonAlreadyExists):
        admin_update_use_case.execute(
            group_uuid=str(group.group_uuid),
            subgroup=None,
            lesson_uuid=str(new_lesson.lesson_uuid),
            old_lesson_uuid=str(old_lesson.lesson_uuid),
        )


@pytest.mark.django_db
def test_admin_update_happy_path_swaps_lessons_and_prunes_old(admin_update_use_case):
    group = GroupModelFactory(has_subgroups=False)
    old_lesson = LessonModelFactory()
    new_lesson = LessonModelFactory()
    GroupLessonModelFactory(group=group, lesson=old_lesson, subgroup=None)

    returned_group, returned_new, returned_old = admin_update_use_case.execute(
        group_uuid=str(group.group_uuid),
        subgroup=None,
        lesson_uuid=str(new_lesson.lesson_uuid),
        old_lesson_uuid=str(old_lesson.lesson_uuid),
    )

    assert returned_new.uuid == str(new_lesson.lesson_uuid)
    assert returned_old.uuid == str(old_lesson.lesson_uuid)
    assert GroupLessonModel.objects.filter(group=group, lesson=new_lesson).exists()
    assert not GroupLessonModel.objects.filter(group=group, lesson=old_lesson).exists()
    assert not LessonModel.objects.filter(pk=old_lesson.pk).exists()


@pytest.mark.django_db
def test_headman_add_invalid_uuid_raises(headman_add_use_case, headman_client):
    GroupModelFactory(headman=headman_client, has_subgroups=False)

    with pytest.raises(InvalidUuidFormatStringException):
        headman_add_use_case.execute(
            headman_email=headman_client.email,
            subgroup=None,
            lesson_uuid="bad",
        )


@pytest.mark.django_db
def test_headman_add_client_not_found_raises(headman_add_use_case):
    with pytest.raises(ClientNotFoundException):
        headman_add_use_case.execute(
            headman_email="ghost@gmail.com",
            subgroup=None,
            lesson_uuid="00000000-0000-0000-0000-000000000000",
        )


@pytest.mark.django_db
def test_headman_add_client_lacks_role_raises(headman_add_use_case):
    not_headman = ClientModelFactory(roles=[RoleModelFactory(id=ClientRole.ADMIN)])
    lesson = LessonModelFactory()

    with pytest.raises(ClientRoleNotMatchingWithRequiredException):
        headman_add_use_case.execute(
            headman_email=not_headman.email,
            subgroup=None,
            lesson_uuid=str(lesson.lesson_uuid),
        )


@pytest.mark.django_db
def test_headman_add_no_group_assignment_raises(headman_add_use_case, headman_client):
    lesson = LessonModelFactory()

    with pytest.raises(HeadmanNotAssignedToAnyGroup):
        headman_add_use_case.execute(
            headman_email=headman_client.email,
            subgroup=None,
            lesson_uuid=str(lesson.lesson_uuid),
        )


@pytest.mark.django_db
def test_headman_add_subgroup_mismatch_raises(headman_add_use_case, headman_client):
    GroupModelFactory(headman=headman_client, has_subgroups=False)
    lesson = LessonModelFactory()

    with pytest.raises(GroupWithoutSubgroupsInvalidSubgroupException):
        headman_add_use_case.execute(
            headman_email=headman_client.email,
            subgroup=Subgroup.A,
            lesson_uuid=str(lesson.lesson_uuid),
        )


@pytest.mark.django_db
def test_headman_add_already_exists_raises(headman_add_use_case, headman_client):
    group = GroupModelFactory(headman=headman_client, has_subgroups=False)
    lesson = LessonModelFactory()
    GroupLessonModelFactory(group=group, lesson=lesson, subgroup=None)

    with pytest.raises(GroupLessonAlreadyExists):
        headman_add_use_case.execute(
            headman_email=headman_client.email,
            subgroup=None,
            lesson_uuid=str(lesson.lesson_uuid),
        )


@pytest.mark.django_db
def test_headman_add_happy_path(headman_add_use_case, headman_client):
    group = GroupModelFactory(headman=headman_client, has_subgroups=False)
    lesson = LessonModelFactory()

    returned_group, returned_lesson = headman_add_use_case.execute(
        headman_email=headman_client.email,
        subgroup=None,
        lesson_uuid=str(lesson.lesson_uuid),
    )

    assert returned_group.uuid == str(group.group_uuid)
    assert returned_lesson.uuid == str(lesson.lesson_uuid)
    assert GroupLessonModel.objects.filter(group=group, lesson=lesson).exists()


@pytest.mark.django_db
def test_headman_remove_invalid_uuid_raises(headman_remove_use_case, headman_client):
    with pytest.raises(InvalidUuidFormatStringException):
        headman_remove_use_case.execute(
            headman_email=headman_client.email,
            subgroup=None,
            lesson_uuid="bad",
        )


@pytest.mark.django_db
def test_headman_remove_client_lacks_role_raises(headman_remove_use_case):
    not_headman = ClientModelFactory(roles=[RoleModelFactory(id=ClientRole.ADMIN)])
    lesson = LessonModelFactory()

    with pytest.raises(ClientRoleNotMatchingWithRequiredException):
        headman_remove_use_case.execute(
            headman_email=not_headman.email,
            subgroup=None,
            lesson_uuid=str(lesson.lesson_uuid),
        )


@pytest.mark.django_db
def test_headman_remove_happy_path(headman_remove_use_case, headman_client):
    group = GroupModelFactory(headman=headman_client, has_subgroups=False)
    lesson = LessonModelFactory()
    GroupLessonModelFactory(group=group, lesson=lesson, subgroup=None)

    returned_group, returned_lesson = headman_remove_use_case.execute(
        headman_email=headman_client.email,
        subgroup=None,
        lesson_uuid=str(lesson.lesson_uuid),
    )

    assert returned_group.uuid == str(group.group_uuid)
    assert returned_lesson.uuid == str(lesson.lesson_uuid)
    assert not GroupLessonModel.objects.filter(group=group, lesson=lesson).exists()


@pytest.mark.django_db
def test_headman_update_invalid_uuid_raises(headman_update_use_case, headman_client):
    with pytest.raises(InvalidUuidFormatStringException):
        headman_update_use_case.execute(
            headman_email=headman_client.email,
            subgroup=None,
            lesson_uuid="bad",
            old_lesson_uuid="bad",
        )


@pytest.mark.django_db
def test_headman_update_client_lacks_role_raises(headman_update_use_case):
    not_headman = ClientModelFactory(roles=[RoleModelFactory(id=ClientRole.ADMIN)])

    with pytest.raises(ClientRoleNotMatchingWithRequiredException):
        headman_update_use_case.execute(
            headman_email=not_headman.email,
            subgroup=None,
            lesson_uuid="00000000-0000-0000-0000-000000000001",
            old_lesson_uuid="00000000-0000-0000-0000-000000000002",
        )


@pytest.mark.django_db
def test_headman_update_happy_path(headman_update_use_case, headman_client):
    group = GroupModelFactory(headman=headman_client, has_subgroups=False)
    old_lesson = LessonModelFactory()
    new_lesson = LessonModelFactory()
    GroupLessonModelFactory(group=group, lesson=old_lesson, subgroup=None)

    returned_group, returned_new, returned_old = headman_update_use_case.execute(
        headman_email=headman_client.email,
        subgroup=None,
        lesson_uuid=str(new_lesson.lesson_uuid),
        old_lesson_uuid=str(old_lesson.lesson_uuid),
    )

    assert returned_new.uuid == str(new_lesson.lesson_uuid)
    assert returned_old.uuid == str(old_lesson.lesson_uuid)
    assert GroupLessonModel.objects.filter(group=group, lesson=new_lesson).exists()
    assert not GroupLessonModel.objects.filter(group=group, lesson=old_lesson).exists()
