from django.db.models import Q

import pytest
from tests.factories.schedule.group import GroupModelFactory
from tests.factories.schedule.group_lesson import GroupLessonModelFactory

from core.apps.common.models import Subgroup
from core.apps.schedule.entities.lesson import Lesson as LessonEntity
from core.apps.schedule.exceptions.lesson import (
    LessonDeleteError,
    LessonNotFoundException,
)
from core.apps.schedule.filters.group import LessonFilter
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


@pytest.mark.django_db
def test_get_or_create_lesson_creates_new(
        lesson_service: BaseLessonService,
        subject_create,
        teacher_create,
        room_create,
        timeslot_create,
):
    subject = subject_create()
    teacher = teacher_create()
    room = room_create()
    timeslot = timeslot_create()
    lesson_entity = LessonEntity(
        subject=subject.to_entity(),
        teacher=teacher.to_entity(),
        room=room.to_entity(),
        timeslot=timeslot.to_entity(),
    )

    result = lesson_service.get_or_create(lesson=lesson_entity)

    assert result.id is not None
    assert result.subject.uuid == subject.subject_uuid
    assert result.teacher.uuid == teacher.teacher_uuid
    assert result.room.uuid == room.room_uuid


@pytest.mark.django_db
def test_get_or_create_lesson_returns_existing(lesson_service: BaseLessonService, create_lesson):
    lesson = create_lesson
    lesson_entity = LessonEntity(
        subject=lesson.subject.to_entity(),
        teacher=lesson.teacher.to_entity(),
        room=lesson.room.to_entity(),
        timeslot=lesson.timeslot.to_entity(),
        type=lesson.type,
    )

    result = lesson_service.get_or_create(lesson=lesson_entity)

    assert result.id == lesson.id
    assert result.uuid == str(lesson.lesson_uuid)


@pytest.mark.django_db
def test_get_by_uuid_lesson_success(lesson_service: BaseLessonService, create_lesson):
    lesson = create_lesson

    found_lesson = lesson_service.get_by_uuid(lesson.lesson_uuid)

    assert found_lesson.uuid == str(lesson.lesson_uuid)


@pytest.mark.django_db
def test_get_by_uuid_lesson_failure(lesson_service: BaseLessonService, build_lesson):
    lesson = build_lesson

    with pytest.raises(LessonNotFoundException):
        lesson_service.get_by_uuid(lesson_uuid=lesson.lesson_uuid)


@pytest.mark.django_db
def test_check_if_teacher_has_lessons_true_when_scheduled(
        lesson_service: BaseLessonService,
        create_lesson,
):
    GroupLessonModelFactory(lesson=create_lesson)

    assert lesson_service.check_if_teacher_has_lessons(teacher_id=create_lesson.teacher_id) is True


@pytest.mark.django_db
def test_check_if_teacher_has_lessons_false_when_only_orphan(
        lesson_service: BaseLessonService,
        create_lesson,
):
    assert lesson_service.check_if_teacher_has_lessons(teacher_id=create_lesson.teacher_id) is False


@pytest.mark.django_db
def test_check_if_subject_has_lessons_true_when_scheduled(
        lesson_service: BaseLessonService,
        create_lesson,
):
    GroupLessonModelFactory(lesson=create_lesson)

    assert lesson_service.check_if_subject_has_lessons(subject_id=create_lesson.subject_id) is True


@pytest.mark.django_db
def test_check_if_subject_has_lessons_false_when_only_orphan(
        lesson_service: BaseLessonService,
        create_lesson,
):
    assert lesson_service.check_if_subject_has_lessons(subject_id=create_lesson.subject_id) is False


@pytest.mark.django_db
def test_check_if_room_has_lessons_true_when_scheduled(
        lesson_service: BaseLessonService,
        create_lesson,
):
    GroupLessonModelFactory(lesson=create_lesson)

    assert lesson_service.check_if_room_has_lessons(room_id=create_lesson.room_id) is True


@pytest.mark.django_db
def test_check_if_room_has_lessons_false_when_only_orphan(
        lesson_service: BaseLessonService,
        create_lesson,
):
    assert lesson_service.check_if_room_has_lessons(room_id=create_lesson.room_id) is False


@pytest.mark.django_db
def test_get_lessons_with_groups_for_teacher_buckets_rows(
        lesson_service: BaseLessonService,
        create_lesson,
):
    group = GroupModelFactory()
    GroupLessonModelFactory(lesson=create_lesson, group=group, subgroup=Subgroup.A)
    GroupLessonModelFactory(lesson=create_lesson, group=group, subgroup=Subgroup.B)

    views = lesson_service.get_lessons_with_groups_for_teacher(
        teacher_id=create_lesson.teacher_id,
        filter_query=LessonFilter(is_even=create_lesson.timeslot.is_even),
    )

    assert len(views) == 1
    assert len(views[0].groups) == 1
    assert sorted(views[0].groups[0].subgroups) == [Subgroup.A, Subgroup.B]


@pytest.mark.django_db
def test_get_lessons_with_groups_for_teacher_empty_when_no_match(
        lesson_service: BaseLessonService,
        create_lesson,
):
    views = lesson_service.get_lessons_with_groups_for_teacher(
        teacher_id=create_lesson.teacher_id,
        filter_query=LessonFilter(is_even=True),
    )

    assert views == []


@pytest.mark.django_db
def test_get_lessons_with_subgroups_for_group_buckets_rows(
        lesson_service: BaseLessonService,
        create_lesson,
):
    group = GroupModelFactory()
    GroupLessonModelFactory(lesson=create_lesson, group=group, subgroup=Subgroup.A)
    GroupLessonModelFactory(lesson=create_lesson, group=group, subgroup=Subgroup.B)

    views = lesson_service.get_lessons_with_subgroups_for_group(
        group_id=group.id,
        filter_query=LessonFilter(is_even=create_lesson.timeslot.is_even),
    )

    assert len(views) == 1
    assert sorted(views[0].subgroups) == [Subgroup.A, Subgroup.B]


@pytest.mark.django_db
def test_get_lessons_with_subgroups_for_group_subgroup_filter(
        lesson_service: BaseLessonService,
        create_lesson,
):
    group = GroupModelFactory()
    GroupLessonModelFactory(lesson=create_lesson, group=group, subgroup=Subgroup.A)

    views = lesson_service.get_lessons_with_subgroups_for_group(
        group_id=group.id,
        filter_query=LessonFilter(is_even=create_lesson.timeslot.is_even, subgroup=Subgroup.A),
    )

    assert len(views) == 1


@pytest.mark.django_db
def test_delete_by_uuid_happy_path(lesson_service: BaseLessonService, create_lesson):
    lesson_service.delete_by_uuid(lesson_uuid=str(create_lesson.lesson_uuid))

    with pytest.raises(LessonNotFoundException):
        lesson_service.get_by_uuid(lesson_uuid=str(create_lesson.lesson_uuid))


@pytest.mark.django_db
def test_delete_by_uuid_raises_when_not_found(lesson_service: BaseLessonService):
    with pytest.raises(LessonDeleteError):
        lesson_service.delete_by_uuid(lesson_uuid="00000000-0000-0000-0000-000000000000")


@pytest.mark.django_db
def test_get_lessons_with_groups_with_raw_query(
        lesson_service: BaseLessonService,
        create_lesson,
):
    group = GroupModelFactory()
    GroupLessonModelFactory(lesson=create_lesson, group=group)

    views = lesson_service.get_lessons_with_groups(
        lesson_filter=Q(lesson__teacher_id=create_lesson.teacher_id),
    )

    assert len(views) == 1
    assert views[0].lesson.uuid == str(create_lesson.lesson_uuid)
