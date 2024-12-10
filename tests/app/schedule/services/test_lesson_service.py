import pytest

from core.apps.schedule.filters.group import LessonFilter
from tests.factories.schedule.lesson import LessonModelFactory

from core.apps.schedule.entities.lesson import Lesson as LessonEntity
from core.apps.schedule.exceptions.lesson import LessonNotFoundException
from core.apps.schedule.services.lesson import BaseLessonService


@pytest.fixture(scope='function')
def create_lesson(lesson_create, subject_create, teacher_create, room_create, timeslot_create):
    subject = subject_create()
    teacher = teacher_create()
    room = room_create()
    timeslot = timeslot_create()
    lesson = lesson_create(
        subject=subject,
        teacher=teacher,
        room=room,
        timeslot=timeslot,
    )
    return lesson


@pytest.fixture(scope='function')
def build_lesson(lesson_build, subject_build, teacher_build, room_build, timeslot_build):
    subject = subject_build()
    teacher = teacher_build()
    room = room_build()
    timeslot = timeslot_build()
    lesson = lesson_build(
        subject=subject,
        teacher=teacher,
        room=room,
        timeslot=timeslot,
    )
    return lesson


@pytest.fixture(scope='function')
def create_lesson_batch_one_teacher(
        lesson_create,
        subject_create_batch,
        teacher_create,
        room_create_batch,
        timeslot_create_batch,
):
    size = 5
    subjects = subject_create_batch(size=size)
    teacher = teacher_create()
    rooms = room_create_batch(size=size)
    timeslots = timeslot_create_batch(size=size, is_even=True)
    lessons = []
    for i in range(size):
        lessons.append(
            lesson_create(
                subject=subjects[i],
                teacher=teacher,
                room=rooms[i],
                timeslot=timeslots[i],
            ),
        )

    return lessons


@pytest.fixture(scope='function')
def create_lesson_batch_two_teachers(
        lesson_create,
        subject_create_batch,
        teacher_create,
        room_create_batch,
        timeslot_create_batch,
):
    size = 5
    size_for_first_teacher = 3
    size_for_second_teacher = 2
    first_teacher = teacher_create()
    second_teacher = teacher_create()
    subjects = subject_create_batch(size=size)
    rooms = room_create_batch(size=size)
    timeslots = timeslot_create_batch(size=size, is_even=True)
    lessons = []
    for i in range(size):
        if i < size_for_first_teacher:
            lessons.append(
                LessonModelFactory.create(
                    subject=subjects[i],
                    teacher=first_teacher,
                    room=rooms[i],
                    timeslot=timeslots[i],
                ),
            )
        else:
            lessons.append(
                LessonModelFactory.create(
                    subject=subjects[i],
                    teacher=second_teacher,
                    room=rooms[i],
                    timeslot=timeslots[i],
                ),
            )

    return lessons, size_for_first_teacher, size_for_second_teacher


@pytest.mark.django_db
def test_save_lesson(lesson_service: BaseLessonService, create_lesson):
    lesson = create_lesson
    lesson_entity = LessonEntity(
        id=lesson.id,
        uuid=lesson.lesson_uuid,
        subject=lesson.subject,
        teacher=lesson.teacher,
        room=lesson.room,
        timeslot=lesson.timeslot,
    )
    saved_lesson = lesson_service.save(lesson=lesson_entity)

    assert saved_lesson.id == lesson.id
    assert saved_lesson.uuid == lesson.lesson_uuid
    assert saved_lesson.subject.uuid == lesson.subject.subject_uuid
    assert saved_lesson.teacher.uuid == lesson.teacher.teacher_uuid
    assert saved_lesson.room.uuid == lesson.room.room_uuid
    assert saved_lesson.timeslot.day == lesson.timeslot.day
    assert saved_lesson.timeslot.ord_number == lesson.timeslot.ord_number
    assert saved_lesson.timeslot.is_even == lesson.timeslot.is_even


@pytest.mark.django_db
def test_get_by_uuid_lesson_success(lesson_service: BaseLessonService, create_lesson):
    lesson = create_lesson

    found_lesson = lesson_service.get_by_uuid(lesson.lesson_uuid)

    assert found_lesson.uuid == lesson.lesson_uuid


@pytest.mark.django_db
def test_get_by_uuid_lesson_failure(lesson_service: BaseLessonService, build_lesson):
    lesson = build_lesson

    with pytest.raises(LessonNotFoundException):
        lesson_service.get_by_uuid(lesson_uuid=lesson.lesson_uuid)


@pytest.mark.django_db
def test_get_by_lesson_entity_lesson_success(lesson_service: BaseLessonService, create_lesson):
    lesson = create_lesson
    lesson_entity = LessonEntity(
        id=lesson.id,
        uuid=lesson.lesson_uuid,
        subject=lesson.subject,
        teacher=lesson.teacher,
        room=lesson.room,
        timeslot=lesson.timeslot,
    )

    found_lesson = lesson_service.get_by_lesson_entity(lesson=lesson_entity)

    assert found_lesson.id == lesson.id
    assert found_lesson.uuid == lesson.lesson_uuid
    assert found_lesson.subject.uuid == lesson.subject.subject_uuid
    assert found_lesson.teacher.uuid == lesson.teacher.teacher_uuid
    assert found_lesson.room.uuid == lesson.room.room_uuid
    assert found_lesson.timeslot.day == lesson.timeslot.day
    assert found_lesson.timeslot.ord_number == lesson.timeslot.ord_number
    assert found_lesson.timeslot.is_even == lesson.timeslot.is_even


@pytest.mark.django_db
def test_get_by_lesson_entity_lesson_failure(lesson_service: BaseLessonService, build_lesson):
    lesson = build_lesson
    lesson_entity = LessonEntity(
        id=lesson.id,
        uuid=lesson.lesson_uuid,
        subject=lesson.subject,
        teacher=lesson.teacher,
        room=lesson.room,
        timeslot=lesson.timeslot,
    )

    with pytest.raises(LessonNotFoundException):
        lesson_service.get_by_lesson_entity(lesson=lesson_entity)


@pytest.mark.django_db
def test_check_exists_lesson_success(lesson_service: BaseLessonService, create_lesson):
    lesson = create_lesson
    lesson_entity = LessonEntity(
        id=lesson.id,
        uuid=lesson.lesson_uuid,
        subject=lesson.subject,
        teacher=lesson.teacher,
        room=lesson.room,
        timeslot=lesson.timeslot,
    )

    assert lesson_service.check_exists(lesson=lesson_entity) is True


@pytest.mark.django_db
def test_check_exists_lesson_failure(lesson_service: BaseLessonService, build_lesson):
    lesson = build_lesson
    lesson_entity = LessonEntity(
        id=lesson.id,
        uuid=lesson.lesson_uuid,
        subject=lesson.subject,
        teacher=lesson.teacher,
        room=lesson.room,
        timeslot=lesson.timeslot,
    )

    assert lesson_service.check_exists(lesson=lesson_entity) is False


@pytest.mark.django_db
def test_get_lessons_for_teacher_lesson_one_teacher(
        lesson_service: BaseLessonService,
        create_lesson_batch_one_teacher,
):
    lessons = create_lesson_batch_one_teacher
    teacher_id = lessons[0].teacher.id
    found_lessons = lesson_service.get_lessons_for_teacher(teacher_id=teacher_id, filter_query=LessonFilter(is_even=True))

    assert len(found_lessons) == len(lessons)
    assert found_lessons[0].teacher.id == teacher_id


@pytest.mark.django_db
def test_get_lessons_for_teacher_lesson_two_teachers(
        lesson_service: BaseLessonService,
        create_lesson_batch_two_teachers,
):
    lessons, size_for_first_teacher, size_for_second_teacher = create_lesson_batch_two_teachers
    teacher_ids = {lesson.teacher.id for lesson in lessons}

    assert len(teacher_ids) == 2

    teacher_lessons = []

    for teacher_id in teacher_ids:
        found_lessons = lesson_service.get_lessons_for_teacher(teacher_id=teacher_id, filter_query=LessonFilter(is_even=True))

        assert found_lessons[0].teacher.id == teacher_id

        teacher_lessons.append(found_lessons)

    assert len(teacher_lessons[0]) == size_for_first_teacher
    assert len(teacher_lessons[1]) == size_for_second_teacher
