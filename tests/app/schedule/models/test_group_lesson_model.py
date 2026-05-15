from django.db import IntegrityError

import pytest
from tests.factories.schedule.group import GroupModelFactory
from tests.factories.schedule.group_lesson import GroupLessonModelFactory
from tests.factories.schedule.lesson import LessonModelFactory

from core.apps.common.models import Subgroup


@pytest.mark.django_db
def test_group_lesson_create():
    gl = GroupLessonModelFactory.create()

    assert gl.pk is not None
    assert gl.group is not None
    assert gl.lesson is not None
    assert gl.subgroup is None
    assert gl.created_at is not None
    assert gl.updated_at is not None


@pytest.mark.django_db
def test_group_lesson_str():
    gl = GroupLessonModelFactory.create()

    assert str(gl.group) in str(gl)


@pytest.mark.django_db
def test_group_lesson_unique_constraint_with_subgroup():
    group = GroupModelFactory.create()
    lesson = LessonModelFactory.create()
    GroupLessonModelFactory.create(group=group, lesson=lesson, subgroup=Subgroup.A)

    with pytest.raises(IntegrityError):
        GroupLessonModelFactory.create(group=group, lesson=lesson, subgroup=Subgroup.A)


@pytest.mark.django_db
def test_group_lesson_unique_constraint_null_subgroup():
    group = GroupModelFactory.create()
    lesson = LessonModelFactory.create()
    GroupLessonModelFactory.create(group=group, lesson=lesson, subgroup=None)

    with pytest.raises(IntegrityError):
        GroupLessonModelFactory.create(group=group, lesson=lesson, subgroup=None)


@pytest.mark.django_db
def test_group_lesson_different_subgroups_allowed():
    group = GroupModelFactory.create()
    lesson = LessonModelFactory.create()
    GroupLessonModelFactory.create(group=group, lesson=lesson, subgroup=Subgroup.A)
    gl_b = GroupLessonModelFactory.create(group=group, lesson=lesson, subgroup=Subgroup.B)

    assert gl_b.pk is not None
