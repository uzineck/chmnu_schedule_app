from django.db import IntegrityError

import pytest
import uuid
from tests.factories.schedule.room import RoomModelFactory

from core.apps.schedule.entities.room import Room as RoomEntity


@pytest.mark.django_db
def test_room_create():
    room = RoomModelFactory.create(number="101", description="Main hall")

    assert room.pk is not None
    assert room.number == "101"
    assert room.description == "Main hall"
    assert room.room_uuid is not None
    assert room.created_at is not None
    assert room.updated_at is not None


@pytest.mark.django_db
def test_room_description_nullable():
    room = RoomModelFactory.create(description=None)

    assert room.pk is not None
    assert room.description is None


@pytest.mark.django_db
def test_room_number_unique_constraint():
    RoomModelFactory.create(number="101")

    with pytest.raises(IntegrityError):
        RoomModelFactory.create(number="101")


@pytest.mark.django_db
def test_room_uuid_unique_constraint():
    fixed_uuid = uuid.uuid4()
    RoomModelFactory.create(room_uuid=fixed_uuid)

    with pytest.raises(IntegrityError):
        RoomModelFactory.create(room_uuid=fixed_uuid)


@pytest.mark.django_db
def test_room_to_entity_maps_all_fields():
    room = RoomModelFactory.create(number="202", description="Lab")

    entity = room.to_entity()

    assert isinstance(entity, RoomEntity)
    assert entity.id == room.id
    assert entity.uuid == str(room.room_uuid)
    assert entity.number == "202"
    assert entity.description == "Lab"
    assert entity.created_at == room.created_at
    assert entity.updated_at == room.updated_at


@pytest.mark.django_db
def test_room_to_entity_with_null_description():
    room = RoomModelFactory.create(description=None)

    entity = room.to_entity()

    assert entity.description is None


def test_room_str():
    room = RoomModelFactory.build(number="303")

    assert str(room) == "303"
