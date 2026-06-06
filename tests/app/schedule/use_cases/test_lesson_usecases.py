from django.core.cache import cache

import pytest
from tests.factories.schedule.lesson import LessonModelFactory

from core.apps.common.models import LessonType
from core.apps.schedule.entities.lesson import Lesson as LessonEntity
from core.apps.schedule.entities.timeslot import Timeslot as TimeslotEntity
from core.apps.schedule.exceptions.lesson import LessonNotFoundException
from core.apps.schedule.exceptions.room import RoomNotFoundException
from core.apps.schedule.exceptions.subject import SubjectNotFoundException
from core.apps.schedule.exceptions.teacher import TeacherNotFoundException
from core.apps.schedule.exceptions.validators.uuid_validator import InvalidUuidFormatStringException
from core.apps.schedule.use_cases.lesson.get_or_create import GetOrCreateLessonUseCase
from core.apps.schedule.use_cases.lesson.update import UpdateLessonUseCase


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def get_or_create_use_case(container) -> GetOrCreateLessonUseCase:
    return container.resolve(GetOrCreateLessonUseCase)


@pytest.fixture
def update_use_case(container) -> UpdateLessonUseCase:
    return container.resolve(UpdateLessonUseCase)


def _build_lesson_entity(timeslot_model) -> LessonEntity:
    timeslot_entity = TimeslotEntity(
        day=timeslot_model.day,
        ord_number=timeslot_model.ord_number,
        is_even=timeslot_model.is_even,
    )
    return LessonEntity(type=LessonType.LECTURE, timeslot=timeslot_entity)


@pytest.mark.django_db
def test_get_or_create_lesson_invalid_uuid_raises(get_or_create_use_case, timeslot_create):
    timeslot = timeslot_create()
    lesson = _build_lesson_entity(timeslot)

    with pytest.raises(InvalidUuidFormatStringException):
        get_or_create_use_case.execute(
            lesson=lesson,
            subject_uuid="bad",
            teacher_uuid="00000000-0000-0000-0000-000000000000",
            room_uuid="00000000-0000-0000-0000-000000000000",
        )


@pytest.mark.django_db
def test_get_or_create_lesson_subject_not_found_raises(
        get_or_create_use_case,
        timeslot_create,
        teacher_create,
        room_create,
):
    teacher = teacher_create()
    room = room_create()
    timeslot = timeslot_create()
    lesson = _build_lesson_entity(timeslot)

    with pytest.raises(SubjectNotFoundException):
        get_or_create_use_case.execute(
            lesson=lesson,
            subject_uuid="00000000-0000-0000-0000-000000000000",
            teacher_uuid=str(teacher.teacher_uuid),
            room_uuid=str(room.room_uuid),
        )


@pytest.mark.django_db
def test_get_or_create_lesson_teacher_not_found_raises(
        get_or_create_use_case,
        timeslot_create,
        subject_create,
        room_create,
):
    subject = subject_create()
    room = room_create()
    timeslot = timeslot_create()
    lesson = _build_lesson_entity(timeslot)

    with pytest.raises(TeacherNotFoundException):
        get_or_create_use_case.execute(
            lesson=lesson,
            subject_uuid=str(subject.subject_uuid),
            teacher_uuid="00000000-0000-0000-0000-000000000000",
            room_uuid=str(room.room_uuid),
        )


@pytest.mark.django_db
def test_get_or_create_lesson_room_not_found_raises(
        get_or_create_use_case,
        timeslot_create,
        subject_create,
        teacher_create,
):
    subject = subject_create()
    teacher = teacher_create()
    timeslot = timeslot_create()
    lesson = _build_lesson_entity(timeslot)

    with pytest.raises(RoomNotFoundException):
        get_or_create_use_case.execute(
            lesson=lesson,
            subject_uuid=str(subject.subject_uuid),
            teacher_uuid=str(teacher.teacher_uuid),
            room_uuid="00000000-0000-0000-0000-000000000000",
        )


@pytest.mark.django_db
def test_get_or_create_lesson_happy_path(
        get_or_create_use_case,
        timeslot_create,
        subject_create,
        teacher_create,
        room_create,
):
    subject = subject_create()
    teacher = teacher_create()
    room = room_create()
    timeslot = timeslot_create()
    lesson = _build_lesson_entity(timeslot)

    created = get_or_create_use_case.execute(
        lesson=lesson,
        subject_uuid=str(subject.subject_uuid),
        teacher_uuid=str(teacher.teacher_uuid),
        room_uuid=str(room.room_uuid),
    )

    assert created.id is not None
    assert created.subject.uuid == str(subject.subject_uuid)


@pytest.mark.django_db
def test_update_lesson_invalid_uuid_raises(update_use_case, timeslot_create):
    timeslot = timeslot_create()
    lesson = _build_lesson_entity(timeslot)

    with pytest.raises(InvalidUuidFormatStringException):
        update_use_case.execute(
            lesson_uuid="bad",
            lesson=lesson,
            subject_uuid="00000000-0000-0000-0000-000000000000",
            teacher_uuid="00000000-0000-0000-0000-000000000000",
            room_uuid="00000000-0000-0000-0000-000000000000",
        )


@pytest.mark.django_db
def test_update_lesson_not_found_raises(update_use_case, timeslot_create):
    timeslot = timeslot_create()
    lesson = _build_lesson_entity(timeslot)

    with pytest.raises(LessonNotFoundException):
        update_use_case.execute(
            lesson_uuid="00000000-0000-0000-0000-000000000000",
            lesson=lesson,
            subject_uuid="00000000-0000-0000-0000-000000000001",
            teacher_uuid="00000000-0000-0000-0000-000000000002",
            room_uuid="00000000-0000-0000-0000-000000000003",
        )


@pytest.mark.django_db
def test_update_lesson_swap_subject_happy_path(
        update_use_case,
        subject_create,
):
    existing_lesson = LessonModelFactory()
    new_subject = subject_create()
    new_timeslot_entity = TimeslotEntity(
        day=existing_lesson.timeslot.day,
        ord_number=existing_lesson.timeslot.ord_number,
        is_even=existing_lesson.timeslot.is_even,
    )
    incoming = LessonEntity(type=existing_lesson.type, timeslot=new_timeslot_entity)

    updated, old = update_use_case.execute(
        lesson_uuid=str(existing_lesson.lesson_uuid),
        lesson=incoming,
        subject_uuid=str(new_subject.subject_uuid),
        teacher_uuid=str(existing_lesson.teacher.teacher_uuid),
        room_uuid=str(existing_lesson.room.room_uuid),
    )

    assert updated.subject.uuid == str(new_subject.subject_uuid)
    assert old.uuid == str(existing_lesson.lesson_uuid)
