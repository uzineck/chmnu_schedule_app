import pytest
from tests.factories.schedule.group import GroupModelFactory
from tests.factories.schedule.group_lesson import GroupLessonModelFactory
from tests.factories.schedule.lesson import LessonModelFactory

from core.apps.common.models import Subgroup
from core.apps.schedule.entities.group_lessons import GroupLesson as GroupLessonEntity
from core.apps.schedule.exceptions.group_lesson import GroupLessonDeleteError
from core.apps.schedule.services.group_lessons import BaseGroupLessonService


@pytest.fixture
def group_lesson_service(container) -> BaseGroupLessonService:
    return container.resolve(BaseGroupLessonService)


@pytest.mark.django_db
def test_check_lesson_belongs_to_any_group_true_when_attached(
        group_lesson_service: BaseGroupLessonService,
):
    lesson = LessonModelFactory()
    GroupLessonModelFactory(lesson=lesson)

    assert group_lesson_service.check_lesson_belongs_to_any_group(lesson_id=lesson.id) is True


@pytest.mark.django_db
def test_check_lesson_belongs_to_any_group_false_when_orphan(
        group_lesson_service: BaseGroupLessonService,
):
    lesson = LessonModelFactory()

    assert group_lesson_service.check_lesson_belongs_to_any_group(lesson_id=lesson.id) is False


@pytest.mark.django_db
def test_delete_group_lesson_happy_path(group_lesson_service: BaseGroupLessonService):
    group = GroupModelFactory()
    lesson = LessonModelFactory()
    gl = GroupLessonModelFactory(group=group, lesson=lesson, subgroup=None)

    entity = GroupLessonEntity(group=group.to_entity(), lesson=lesson.to_entity(), subgroup=None)
    group_lesson_service.delete(group_lesson=entity)

    assert not type(gl).objects.filter(pk=gl.pk).exists()


@pytest.mark.django_db
def test_delete_group_lesson_raises_when_missing(group_lesson_service: BaseGroupLessonService):
    group = GroupModelFactory()
    lesson = LessonModelFactory()
    entity = GroupLessonEntity(group=group.to_entity(), lesson=lesson.to_entity(), subgroup=None)

    with pytest.raises(GroupLessonDeleteError):
        group_lesson_service.delete(group_lesson=entity)


@pytest.mark.django_db
def test_get_subgroup_from_group_lesson_returns_subgroups(
        group_lesson_service: BaseGroupLessonService,
):
    group = GroupModelFactory()
    lesson = LessonModelFactory()
    GroupLessonModelFactory(group=group, lesson=lesson, subgroup=Subgroup.A)
    GroupLessonModelFactory(group=group, lesson=lesson, subgroup=Subgroup.B)

    result = group_lesson_service.get_subgroup_from_group_lesson(
        group_id=group.id,
        lesson_id=lesson.id,
    )

    assert result is not None
    assert sorted(result) == [Subgroup.A, Subgroup.B]


@pytest.mark.django_db
def test_get_subgroup_from_group_lesson_returns_none_when_only_null_subgroups(
        group_lesson_service: BaseGroupLessonService,
):
    group = GroupModelFactory()
    lesson = LessonModelFactory()
    GroupLessonModelFactory(group=group, lesson=lesson, subgroup=None)

    result = group_lesson_service.get_subgroup_from_group_lesson(
        group_id=group.id,
        lesson_id=lesson.id,
    )

    assert result is None


@pytest.mark.django_db
def test_get_subgroup_from_group_lesson_returns_none_when_no_rows(
        group_lesson_service: BaseGroupLessonService,
):
    group = GroupModelFactory()
    lesson = LessonModelFactory()

    result = group_lesson_service.get_subgroup_from_group_lesson(
        group_id=group.id,
        lesson_id=lesson.id,
    )

    assert result is None
