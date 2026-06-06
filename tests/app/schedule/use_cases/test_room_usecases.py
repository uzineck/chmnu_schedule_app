from django.core.cache import cache

import pytest
from tests.factories.schedule.group_lesson import GroupLessonModelFactory
from tests.factories.schedule.lesson import LessonModelFactory

from core.api.filters import PaginationIn
from core.apps.common.filters import SearchFilter
from core.apps.schedule.exceptions.room import (
    OldAndNewRoomDescriptionsAreSimilarException,
    RoomAlreadyExistException,
    RoomIsUsedInLessonsException,
    RoomNotFoundException,
)
from core.apps.schedule.exceptions.validators.uuid_validator import InvalidUuidFormatStringException
from core.apps.schedule.use_cases.room.create import CreateRoomUseCase
from core.apps.schedule.use_cases.room.delete import DeleteRoomUseCase
from core.apps.schedule.use_cases.room.get_all import GetAllRoomsUseCase
from core.apps.schedule.use_cases.room.get_list import GetRoomListUseCase
from core.apps.schedule.use_cases.room.update_description import UpdateRoomDescriptionUseCase
from core.apps.schedule.use_cases.room.update_number import UpdateRoomNumberUseCase


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def get_all_use_case(container) -> GetAllRoomsUseCase:
    return container.resolve(GetAllRoomsUseCase)


@pytest.fixture
def get_list_use_case(container) -> GetRoomListUseCase:
    return container.resolve(GetRoomListUseCase)


@pytest.fixture
def create_use_case(container) -> CreateRoomUseCase:
    return container.resolve(CreateRoomUseCase)


@pytest.fixture
def delete_use_case(container) -> DeleteRoomUseCase:
    return container.resolve(DeleteRoomUseCase)


@pytest.fixture
def update_number_use_case(container) -> UpdateRoomNumberUseCase:
    return container.resolve(UpdateRoomNumberUseCase)


@pytest.fixture
def update_description_use_case(container) -> UpdateRoomDescriptionUseCase:
    return container.resolve(UpdateRoomDescriptionUseCase)


@pytest.mark.django_db
def test_get_all_rooms_returns_list(get_all_use_case, room_create_batch):
    room_create_batch(size=3)

    result = get_all_use_case.execute()

    assert len(result) == 3


@pytest.mark.django_db
def test_get_room_list_returns_paginated(get_list_use_case, room_create_batch):
    room_create_batch(size=4)

    items, count = get_list_use_case.execute(
        filters=SearchFilter(),
        pagination_in=PaginationIn(offset=0, limit=10),
    )

    assert count == 4
    assert len(list(items)) == 4


@pytest.mark.django_db
def test_create_room_happy_path(create_use_case, room_build):
    room = room_build()

    created = create_use_case.execute(number=room.number)

    assert created.number == room.number


@pytest.mark.django_db
def test_create_room_already_exists_raises(create_use_case, room_create):
    existing = room_create()

    with pytest.raises(RoomAlreadyExistException):
        create_use_case.execute(number=existing.number)


@pytest.mark.django_db
def test_create_room_restores_soft_deleted(create_use_case, delete_use_case, room_create):
    original = room_create()
    delete_use_case.execute(room_uuid=str(original.room_uuid))

    restored = create_use_case.execute(number=original.number)

    assert restored.id == original.id
    assert restored.is_active is True


@pytest.mark.django_db
def test_delete_room_invalid_uuid_raises(delete_use_case):
    with pytest.raises(InvalidUuidFormatStringException):
        delete_use_case.execute(room_uuid="not-a-uuid")


@pytest.mark.django_db
def test_delete_room_not_found_raises(delete_use_case):
    with pytest.raises(RoomNotFoundException):
        delete_use_case.execute(room_uuid="00000000-0000-0000-0000-000000000000")


@pytest.mark.django_db
def test_delete_room_used_in_lessons_raises(delete_use_case, room_create):
    room = room_create()
    lesson = LessonModelFactory(room=room)
    GroupLessonModelFactory(lesson=lesson)

    with pytest.raises(RoomIsUsedInLessonsException):
        delete_use_case.execute(room_uuid=str(room.room_uuid))


@pytest.mark.django_db
def test_delete_room_soft_deletes(delete_use_case, room_create, room_service):
    room = room_create()

    delete_use_case.execute(room_uuid=str(room.room_uuid))

    found = room_service.find_any_by_number(room_number=room.number)
    assert found is not None
    assert found.is_active is False


@pytest.mark.django_db
def test_update_room_number_invalid_uuid_raises(update_number_use_case):
    with pytest.raises(InvalidUuidFormatStringException):
        update_number_use_case.execute(room_uuid="bad", new_number="999")


@pytest.mark.django_db
def test_update_room_number_already_taken_raises(update_number_use_case, room_create_batch):
    r1, r2 = room_create_batch(size=2)

    with pytest.raises(RoomAlreadyExistException):
        update_number_use_case.execute(room_uuid=str(r1.room_uuid), new_number=r2.number)


@pytest.mark.django_db
def test_update_room_number_happy_path(update_number_use_case, room_create):
    room = room_create()

    updated = update_number_use_case.execute(room_uuid=str(room.room_uuid), new_number="999-9")

    assert updated.number == "999-9"
    assert updated.id == room.id


@pytest.mark.django_db
def test_update_room_description_same_as_old_raises(update_description_use_case, room_create):
    room = room_create(description="Whiteboard + projector")

    with pytest.raises(OldAndNewRoomDescriptionsAreSimilarException):
        update_description_use_case.execute(
            room_uuid=str(room.room_uuid),
            description="Whiteboard + projector",
        )


@pytest.mark.django_db
def test_update_room_description_happy_path(update_description_use_case, room_create):
    room = room_create(description="Old desc")

    updated = update_description_use_case.execute(
        room_uuid=str(room.room_uuid),
        description="New desc with projector",
    )

    assert updated.description == "New desc with projector"
    assert updated.id == room.id
