from django.db import IntegrityError

import pytest
import uuid
from tests.factories.client.client import ClientModelFactory
from tests.factories.schedule.faculty import FacultyModelFactory
from tests.factories.schedule.group import GroupModelFactory

from core.apps.schedule.entities.group import Group as GroupEntity


@pytest.mark.django_db
def test_group_create():
    group = GroupModelFactory.create()

    assert group.pk is not None
    assert group.group_uuid is not None
    assert group.number is not None
    assert group.created_at is not None
    assert group.updated_at is not None


@pytest.mark.django_db
def test_group_uuid_unique_constraint():
    fixed_uuid = uuid.uuid4()
    GroupModelFactory.create(group_uuid=fixed_uuid)

    with pytest.raises(IntegrityError):
        GroupModelFactory.create(group_uuid=fixed_uuid)


@pytest.mark.django_db
def test_group_number_unique_constraint():
    GroupModelFactory.create(number="ПМ-101")

    with pytest.raises(IntegrityError):
        GroupModelFactory.create(number="ПМ-101")


@pytest.mark.django_db
def test_group_str_returns_number():
    group = GroupModelFactory.create(number="ПМ-101")

    assert str(group) == "ПМ-101"


@pytest.mark.django_db
def test_group_to_entity_with_faculty_and_headman():
    faculty = FacultyModelFactory.create()
    headman = ClientModelFactory.create()
    group = GroupModelFactory.create(faculty=faculty, headman=headman)

    entity = group.to_entity()

    assert isinstance(entity, GroupEntity)
    assert entity.id == group.id
    assert entity.uuid == str(group.group_uuid)
    assert entity.number == group.number
    assert entity.faculty is not None
    assert entity.headman is not None


@pytest.mark.django_db
def test_group_to_entity_without_faculty_and_headman():
    group = GroupModelFactory.create(faculty=None, headman=None)

    entity = group.to_entity()

    assert isinstance(entity, GroupEntity)
    assert entity.faculty is None
    assert entity.headman is None
