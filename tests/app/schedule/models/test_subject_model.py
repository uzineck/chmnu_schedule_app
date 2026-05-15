from django.db import IntegrityError

import pytest
import uuid
from tests.factories.schedule.subject import SubjectModelFactory

from core.apps.schedule.entities.subject import Subject as SubjectEntity


@pytest.mark.django_db
def test_subject_create():
    subject = SubjectModelFactory.create(title="Математика", slug="matematika")

    assert subject.pk is not None
    assert subject.title == "Математика"
    assert subject.slug == "matematika"
    assert subject.subject_uuid is not None
    assert subject.created_at is not None
    assert subject.updated_at is not None


@pytest.mark.django_db
def test_subject_title_unique_constraint():
    SubjectModelFactory.create(title="Фізика", slug="fizika")

    with pytest.raises(IntegrityError):
        SubjectModelFactory.create(title="Фізика", slug="fizika-2")


@pytest.mark.django_db
def test_subject_slug_unique_constraint():
    SubjectModelFactory.create(title="Хімія", slug="himiya")

    with pytest.raises(IntegrityError):
        SubjectModelFactory.create(title="Хімія 2", slug="himiya")


@pytest.mark.django_db
def test_subject_uuid_unique_constraint():
    fixed_uuid = uuid.uuid4()
    SubjectModelFactory.create(subject_uuid=fixed_uuid)

    with pytest.raises(IntegrityError):
        SubjectModelFactory.create(subject_uuid=fixed_uuid)


@pytest.mark.django_db
def test_subject_to_entity_maps_all_fields():
    subject = SubjectModelFactory.create(title="Біологія", slug="biologiya")

    entity = subject.to_entity()

    assert isinstance(entity, SubjectEntity)
    assert entity.id == subject.id
    assert entity.uuid == str(subject.subject_uuid)
    assert entity.title == "Біологія"
    assert entity.slug == "biologiya"
    assert entity.created_at == subject.created_at
    assert entity.updated_at == subject.updated_at


def test_subject_str():
    subject = SubjectModelFactory.build(title="Історія")

    assert str(subject) == "Історія"
