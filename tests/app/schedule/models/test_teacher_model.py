from django.db import IntegrityError

import pytest
import uuid
from tests.factories.schedule.teacher import TeacherModelFactory

from core.apps.common.models import TeachersDegree
from core.apps.schedule.entities.teacher import Teacher as TeacherEntity


@pytest.mark.django_db
def test_teacher_create():
    teacher = TeacherModelFactory.create(
        first_name="Іван",
        last_name="Шевченко",
        middle_name="Олегович",
        rank=TeachersDegree.PROFESSOR,
        is_active=True,
    )

    assert teacher.pk is not None
    assert teacher.first_name == "Іван"
    assert teacher.last_name == "Шевченко"
    assert teacher.middle_name == "Олегович"
    assert teacher.rank == TeachersDegree.PROFESSOR
    assert teacher.is_active is True
    assert teacher.teacher_uuid is not None
    assert teacher.created_at is not None
    assert teacher.updated_at is not None


@pytest.mark.django_db
def test_teacher_uuid_unique_constraint():
    fixed_uuid = uuid.uuid4()
    TeacherModelFactory.create(teacher_uuid=fixed_uuid)

    with pytest.raises(IntegrityError):
        TeacherModelFactory.create(teacher_uuid=fixed_uuid)


@pytest.mark.django_db
def test_teacher_same_name_allowed():
    TeacherModelFactory.create(first_name="Іван", last_name="Коваль", middle_name="Петрович")
    teacher2 = TeacherModelFactory.create(first_name="Іван", last_name="Коваль", middle_name="Петрович")

    assert teacher2.pk is not None


@pytest.mark.django_db
def test_teacher_is_active_default_true():
    teacher = TeacherModelFactory.create()

    assert teacher.is_active is True


@pytest.mark.django_db
def test_teacher_to_entity_maps_all_fields():
    teacher = TeacherModelFactory.create(
        first_name="Олена",
        last_name="Бондаренко",
        middle_name="Василівна",
        rank=TeachersDegree.LECTURER,
        is_active=False,
    )

    entity = teacher.to_entity()

    assert isinstance(entity, TeacherEntity)
    assert entity.id == teacher.id
    assert entity.uuid == str(teacher.teacher_uuid)
    assert entity.first_name == "Олена"
    assert entity.last_name == "Бондаренко"
    assert entity.middle_name == "Василівна"
    assert entity.rank == TeachersDegree.LECTURER
    assert entity.is_active is False
    assert entity.created_at == teacher.created_at
    assert entity.updated_at == teacher.updated_at


def test_teacher_str_full_name():
    teacher = TeacherModelFactory.build(
        first_name="Іван",
        last_name="Шевченко",
        middle_name="Олегович",
    )

    assert str(teacher) == "Шевченко І. О."


def test_teacher_str_missing_middle_name():
    teacher = TeacherModelFactory.build(
        first_name="Іван",
        last_name="Шевченко",
        middle_name="",
    )

    assert str(teacher) == "Шевченко І."


def test_teacher_str_missing_first_name():
    teacher = TeacherModelFactory.build(
        first_name="",
        last_name="Шевченко",
        middle_name="Олегович",
    )

    assert str(teacher) == "Шевченко О."
