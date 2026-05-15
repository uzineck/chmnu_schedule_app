from django.db import IntegrityError

import pytest
import uuid
from tests.factories.schedule.faculty import FacultyModelFactory

from core.apps.schedule.entities.faculty import Faculty as FacultyEntity


@pytest.mark.django_db
def test_faculty_create():
    faculty = FacultyModelFactory.create(code_name="ФІТ", name="Факультет інформаційних технологій")

    assert faculty.pk is not None
    assert faculty.code_name == "ФІТ"
    assert faculty.name == "Факультет інформаційних технологій"
    assert faculty.faculty_uuid is not None
    assert faculty.created_at is not None
    assert faculty.updated_at is not None


@pytest.mark.django_db
def test_faculty_code_name_unique_constraint():
    FacultyModelFactory.create(code_name="ФІТ")

    with pytest.raises(IntegrityError):
        FacultyModelFactory.create(code_name="ФІТ")


@pytest.mark.django_db
def test_faculty_uuid_unique_constraint():
    fixed_uuid = uuid.uuid4()
    FacultyModelFactory.create(faculty_uuid=fixed_uuid)

    with pytest.raises(IntegrityError):
        FacultyModelFactory.create(faculty_uuid=fixed_uuid)


@pytest.mark.django_db
def test_faculty_same_name_different_code_name_allowed():
    FacultyModelFactory.create(code_name="ФІТ", name="Факультет")
    faculty2 = FacultyModelFactory.create(code_name="ФЕК", name="Факультет")

    assert faculty2.pk is not None


@pytest.mark.django_db
def test_faculty_to_entity_maps_all_fields():
    faculty = FacultyModelFactory.create(code_name="ФМФ", name="Фізико-математичний факультет")

    entity = faculty.to_entity()

    assert isinstance(entity, FacultyEntity)
    assert entity.id == faculty.id
    assert entity.uuid == str(faculty.faculty_uuid)
    assert entity.code_name == "ФМФ"
    assert entity.name == "Фізико-математичний факультет"
    assert entity.created_at == faculty.created_at
    assert entity.updated_at == faculty.updated_at


def test_faculty_str():
    faculty = FacultyModelFactory.build(code_name="ФЕФ")

    assert str(faculty) == "ФЕФ"
