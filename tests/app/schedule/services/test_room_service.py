import pytest

from core.api.filters import (
    PaginationIn,
    SearchFilter,
)
from core.apps.schedule.exceptions.room import (
    RoomAlreadyExistException,
    RoomDeleteException,
    RoomNotFoundException,
    RoomUpdateException,
)
from core.apps.schedule.services.room import BaseRoomService


@pytest.mark.django_db
def test_create_room_success(room_service: BaseRoomService, room_build):
    room = room_build()

    created_room = room_service.create(
        number=room.number,
    )

    assert created_room.number == room.number, f'{room.number}'
    assert created_room.description is None


@pytest.mark.django_db
def test_create_room_already_exists_failure(room_service: BaseRoomService, room_create):
    room = room_create()

    with pytest.raises(RoomAlreadyExistException):
        room_service.create(number=room.number)


@pytest.mark.django_db
def test_get_count_room_zero(room_service: BaseRoomService):
    room_count = room_service.get_count(filters=SearchFilter())
    assert room_count == 0, f"{room_count=}"


@pytest.mark.django_db
def test_get_count_room_exist(room_service: BaseRoomService, room_create_batch):
    expected_count = 5
    room_create_batch(size=expected_count)

    room_count = room_service.get_count(filters=SearchFilter())
    assert room_count == expected_count, f"{room_count=}"


@pytest.mark.django_db
def test_get_all_rooms_success(room_service: BaseRoomService, room_create_batch):
    expected_count = 5
    rooms = room_create_batch(size=expected_count)
    room_numbers = {room.number for room in rooms}

    fetched_rooms = room_service.get_all()
    fetched_numbers = {room.number for room in fetched_rooms}

    assert len(fetched_numbers) == expected_count, f"{fetched_numbers=}"
    assert room_numbers == fetched_numbers, f"{room_numbers=}"


@pytest.mark.django_db
def test_get_list_rooms_success(room_service: BaseRoomService, room_create_batch):
    expected_count = 5
    rooms = room_create_batch(size=expected_count)
    room_numbers = {room.number for room in rooms}

    fetched_rooms = room_service.get_list(filters=SearchFilter(), pagination=PaginationIn())
    fetched_numbers = {room.number for room in fetched_rooms}

    assert len(fetched_numbers) == expected_count, f"{fetched_numbers=}"
    assert room_numbers == fetched_numbers, f"{room_numbers=}"


@pytest.mark.django_db
def test_get_by_uuid_room_success(room_service: BaseRoomService, room_create):
    room = room_create()

    found_room = room_service.get_by_uuid(room.room_uuid)

    assert room.room_uuid == found_room.uuid
    assert room.number == found_room.number


@pytest.mark.django_db
def test_get_by_uuid_room_not_found_failure(room_service: BaseRoomService, room_build):
    room = room_build()

    with pytest.raises(RoomNotFoundException):
        room_service.get_by_uuid(room_uuid=room.room_uuid)


@pytest.mark.django_db
def test_get_by_id_room_success(room_service: BaseRoomService, room_create):
    room = room_create()

    found_room = room_service.get_by_id(room.id)

    assert room.id == found_room.id
    assert room.number == found_room.number


@pytest.mark.django_db
def test_get_by_id_room_not_found_failure(room_service: BaseRoomService, room_build):
    room = room_build()

    with pytest.raises(RoomNotFoundException):
        room_service.get_by_id(room_id=room.id)


@pytest.mark.django_db
def test_check_exists_by_number_room_true(room_service: BaseRoomService, room_create):
    room = room_create()

    assert room_service.check_exists_by_number(room_number=room.number) is True


@pytest.mark.django_db
def test_check_exists_by_number_room_false(room_service: BaseRoomService, room_build):
    room = room_build()

    assert room_service.check_exists_by_number(room_number=room.number) is False


@pytest.mark.django_db
def test_update_room_number_success(room_service: BaseRoomService, room_create, room_build):
    room = room_create()

    new_room = room_build()

    assert room_service.update_number(room_id=room.id, number=new_room.number) is None


@pytest.mark.django_db
def test_update_room_name_failure(room_service: BaseRoomService, room_build):
    room = room_build()

    with pytest.raises(RoomUpdateException):
        room_service.update_number(room_id=room.id, number=room.number)


@pytest.mark.django_db
def test_update_room_description_success(room_service: BaseRoomService, room_create):
    room = room_create()

    description = "New description"

    assert room_service.update_description(room_id=room.id, description=description) is None


@pytest.mark.django_db
def test_update_room_description_failure(room_service: BaseRoomService, room_build):
    room = room_build()

    description = "New description"

    with pytest.raises(RoomUpdateException):
        room_service.update_description(room_id=room.id, description=description)


@pytest.mark.django_db
def test_delete_room_success(room_service: BaseRoomService, room_create):
    room = room_create()

    assert room_service.delete(room_id=room.id) is None


@pytest.mark.django_db
def test_delete_room_failure(room_service: BaseRoomService, room_build):
    room = room_build()

    with pytest.raises(RoomDeleteException):
        room_service.delete(room_id=room.id)
