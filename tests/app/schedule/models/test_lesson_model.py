from django.db import IntegrityError

import pytest
import uuid
from tests.factories.schedule.lesson import LessonModelFactory

from core.apps.schedule.entities.lesson import Lesson as LessonEntity


@pytest.mark.django_db
def test_lesson_create():
    lesson = LessonModelFactory.create()

    assert lesson.pk is not None
    assert lesson.lesson_uuid is not None
    assert lesson.type is not None
    assert lesson.created_at is not None
    assert lesson.updated_at is not None


@pytest.mark.django_db
def test_lesson_uuid_unique_constraint():
    fixed_uuid = uuid.uuid4()
    LessonModelFactory.create(lesson_uuid=fixed_uuid)

    with pytest.raises(IntegrityError):
        LessonModelFactory.create(lesson_uuid=fixed_uuid)


@pytest.mark.django_db
def test_lesson_to_entity_maps_all_fields():
    lesson = LessonModelFactory.create()

    entity = lesson.to_entity()

    assert isinstance(entity, LessonEntity)
    assert entity.id == lesson.id
    assert entity.uuid == str(lesson.lesson_uuid)
    assert entity.type == lesson.type
    assert entity.created_at == lesson.created_at
    assert entity.updated_at == lesson.updated_at


@pytest.mark.django_db
def test_lesson_str():
    lesson = LessonModelFactory.create()

    result = str(lesson)

    assert lesson.type in result
    assert str(lesson.subject) in result
