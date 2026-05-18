import pytest
from django.core.cache import cache
from tests.factories.schedule.group_lesson import GroupLessonModelFactory
from tests.factories.schedule.lesson import LessonModelFactory

from core.api.filters import PaginationIn
from core.apps.common.models import TeachersDegree
from core.apps.schedule.filters.teacher import TeacherFilter
from core.apps.schedule.exceptions.teacher import (
    OldAndNewTeacherRanksAreSimilarException,
    TeacherAlreadyExistsException,
    TeacherIsUsedInLessonsException,
    TeacherNotFoundException,
)
from core.apps.schedule.exceptions.validators.uuid_validator import InvalidUuidFormatStringException
from core.apps.schedule.filters.group import LessonFilter
from core.apps.schedule.use_cases.teacher.create import CreateTeacherUseCase
from core.apps.schedule.use_cases.teacher.delete import DeleteTeacherUseCase
from core.apps.schedule.use_cases.teacher.get_all import GetAllTeachersUseCase
from core.apps.schedule.use_cases.teacher.get_list import GetTeacherListUseCase
from core.apps.schedule.use_cases.teacher.get_teacher_lessons import GetLessonsForTeacherUseCase
from core.apps.schedule.use_cases.teacher.update_name import UpdateTeacherNameUseCase
from core.apps.schedule.use_cases.teacher.update_rank import UpdateTeacherRankUseCase


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def get_all_use_case(container) -> GetAllTeachersUseCase:
    return container.resolve(GetAllTeachersUseCase)


@pytest.fixture
def get_list_use_case(container) -> GetTeacherListUseCase:
    return container.resolve(GetTeacherListUseCase)


@pytest.fixture
def get_lessons_use_case(container) -> GetLessonsForTeacherUseCase:
    return container.resolve(GetLessonsForTeacherUseCase)


@pytest.fixture
def create_use_case(container) -> CreateTeacherUseCase:
    return container.resolve(CreateTeacherUseCase)


@pytest.fixture
def delete_use_case(container) -> DeleteTeacherUseCase:
    return container.resolve(DeleteTeacherUseCase)


@pytest.fixture
def update_name_use_case(container) -> UpdateTeacherNameUseCase:
    return container.resolve(UpdateTeacherNameUseCase)


@pytest.fixture
def update_rank_use_case(container) -> UpdateTeacherRankUseCase:
    return container.resolve(UpdateTeacherRankUseCase)


@pytest.mark.django_db
def test_get_all_teachers_returns_list(get_all_use_case, teacher_create_batch):
    teacher_create_batch(size=3)

    result = get_all_use_case.execute()

    assert len(result) == 3


@pytest.mark.django_db
def test_get_teacher_list_returns_paginated(get_list_use_case, teacher_create_batch):
    teacher_create_batch(size=4)

    items, count = get_list_use_case.execute(
        filters=TeacherFilter(),
        pagination_in=PaginationIn(offset=0, limit=10),
    )

    assert count == 4
    assert len(list(items)) == 4


@pytest.mark.django_db
def test_get_teacher_lessons_invalid_uuid_raises(get_lessons_use_case):
    with pytest.raises(InvalidUuidFormatStringException):
        get_lessons_use_case.execute(teacher_uuid="bad", filters=LessonFilter(is_even=True))


@pytest.mark.django_db
def test_get_teacher_lessons_happy_path(get_lessons_use_case, teacher_create):
    teacher = teacher_create()

    returned_teacher, views = get_lessons_use_case.execute(
        teacher_uuid=str(teacher.teacher_uuid),
        filters=LessonFilter(is_even=True),
    )

    assert returned_teacher.uuid == str(teacher.teacher_uuid)
    assert isinstance(views, list)


@pytest.mark.django_db
def test_create_teacher_happy_path(create_use_case, teacher_build):
    teacher = teacher_build()

    created = create_use_case.execute(
        first_name=teacher.first_name,
        last_name=teacher.last_name,
        middle_name=teacher.middle_name,
        rank=TeachersDegree.PROFESSOR,
    )

    assert created.first_name == teacher.first_name
    assert created.rank == TeachersDegree.PROFESSOR


@pytest.mark.django_db
def test_create_teacher_already_exists_raises(create_use_case, teacher_create):
    existing = teacher_create()

    with pytest.raises(TeacherAlreadyExistsException):
        create_use_case.execute(
            first_name=existing.first_name,
            last_name=existing.last_name,
            middle_name=existing.middle_name,
            rank=TeachersDegree.PROFESSOR,
        )


@pytest.mark.django_db
def test_create_teacher_restores_soft_deleted(create_use_case, delete_use_case, teacher_create):
    original = teacher_create()
    delete_use_case.execute(teacher_uuid=str(original.teacher_uuid))

    restored = create_use_case.execute(
        first_name=original.first_name,
        last_name=original.last_name,
        middle_name=original.middle_name,
        rank=TeachersDegree.ASSOCIATE_PROFESSOR,
    )

    assert restored.id == original.id
    assert restored.is_active is True
    assert restored.rank == TeachersDegree.ASSOCIATE_PROFESSOR


@pytest.mark.django_db
def test_delete_teacher_invalid_uuid_raises(delete_use_case):
    with pytest.raises(InvalidUuidFormatStringException):
        delete_use_case.execute(teacher_uuid="bad-uuid")


@pytest.mark.django_db
def test_delete_teacher_not_found_raises(delete_use_case):
    with pytest.raises(TeacherNotFoundException):
        delete_use_case.execute(teacher_uuid="00000000-0000-0000-0000-000000000000")


@pytest.mark.django_db
def test_delete_teacher_used_in_lessons_raises(delete_use_case, teacher_create):
    teacher = teacher_create()
    lesson = LessonModelFactory(teacher=teacher)
    GroupLessonModelFactory(lesson=lesson)

    with pytest.raises(TeacherIsUsedInLessonsException):
        delete_use_case.execute(teacher_uuid=str(teacher.teacher_uuid))


@pytest.mark.django_db
def test_delete_teacher_soft_deletes(delete_use_case, teacher_create, teacher_service):
    teacher = teacher_create()

    delete_use_case.execute(teacher_uuid=str(teacher.teacher_uuid))

    found = teacher_service.find_any_by_full_name(
        first_name=teacher.first_name,
        last_name=teacher.last_name,
        middle_name=teacher.middle_name,
    )
    assert found is not None
    assert found.is_active is False


@pytest.mark.django_db
def test_update_teacher_name_invalid_uuid_raises(update_name_use_case):
    with pytest.raises(InvalidUuidFormatStringException):
        update_name_use_case.execute(
            teacher_uuid="bad",
            first_name="A",
            last_name="B",
            middle_name="C",
        )


@pytest.mark.django_db
def test_update_teacher_name_already_taken_raises(update_name_use_case, teacher_create_batch):
    t1, t2 = teacher_create_batch(size=2)

    with pytest.raises(TeacherAlreadyExistsException):
        update_name_use_case.execute(
            teacher_uuid=str(t1.teacher_uuid),
            first_name=t2.first_name,
            last_name=t2.last_name,
            middle_name=t2.middle_name,
        )


@pytest.mark.django_db
def test_update_teacher_name_happy_path(update_name_use_case, teacher_create):
    teacher = teacher_create()

    updated = update_name_use_case.execute(
        teacher_uuid=str(teacher.teacher_uuid),
        first_name="Іван",
        last_name="Іваненко",
        middle_name="Іванович",
    )

    assert updated.first_name == "Іван"
    assert updated.id == teacher.id


@pytest.mark.django_db
def test_update_teacher_rank_same_as_old_raises(update_rank_use_case, teacher_create):
    # Reachable here: rank has no AlreadyExists check, so Similar fires correctly.
    teacher = teacher_create(rank=TeachersDegree.PROFESSOR)

    with pytest.raises(OldAndNewTeacherRanksAreSimilarException):
        update_rank_use_case.execute(
            teacher_uuid=str(teacher.teacher_uuid),
            rank=TeachersDegree.PROFESSOR,
        )


@pytest.mark.django_db
def test_update_teacher_rank_happy_path(update_rank_use_case, teacher_create):
    teacher = teacher_create(rank=TeachersDegree.ASSOCIATE_PROFESSOR)

    updated = update_rank_use_case.execute(
        teacher_uuid=str(teacher.teacher_uuid),
        rank=TeachersDegree.PROFESSOR,
    )

    assert updated.rank == TeachersDegree.PROFESSOR
    assert updated.id == teacher.id
