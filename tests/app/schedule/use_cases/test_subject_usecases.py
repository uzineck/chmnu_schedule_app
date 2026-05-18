import pytest
from django.core.cache import cache
from tests.factories.schedule.group_lesson import GroupLessonModelFactory
from tests.factories.schedule.lesson import LessonModelFactory

from core.api.filters import PaginationIn
from core.apps.common.filters import SearchFilter
from core.apps.schedule.exceptions.subject import (
    SubjectAlreadyExistException,
    SubjectIsUsedInLessonsException,
    SubjectNotFoundException,
)
from core.apps.schedule.exceptions.validators.uuid_validator import InvalidUuidFormatStringException
from core.apps.schedule.use_cases.subject.create import CreateSubjectUseCase
from core.apps.schedule.use_cases.subject.delete import DeleteSubjectUseCase
from core.apps.schedule.use_cases.subject.get_all import GetAllSubjectsUseCase
from core.apps.schedule.use_cases.subject.get_list import GetSubjectListUseCase
from core.apps.schedule.use_cases.subject.update import UpdateSubjectUseCase


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def get_all_use_case(container) -> GetAllSubjectsUseCase:
    return container.resolve(GetAllSubjectsUseCase)


@pytest.fixture
def get_list_use_case(container) -> GetSubjectListUseCase:
    return container.resolve(GetSubjectListUseCase)


@pytest.fixture
def create_use_case(container) -> CreateSubjectUseCase:
    return container.resolve(CreateSubjectUseCase)


@pytest.fixture
def delete_use_case(container) -> DeleteSubjectUseCase:
    return container.resolve(DeleteSubjectUseCase)


@pytest.fixture
def update_use_case(container) -> UpdateSubjectUseCase:
    return container.resolve(UpdateSubjectUseCase)


@pytest.mark.django_db
def test_get_all_subjects_returns_list(get_all_use_case, subject_create_batch):
    subject_create_batch(size=3)

    result = get_all_use_case.execute()

    assert len(result) == 3


@pytest.mark.django_db
def test_get_subject_list_returns_paginated(get_list_use_case, subject_create_batch):
    subject_create_batch(size=4)

    items, count = get_list_use_case.execute(
        filters=SearchFilter(),
        pagination_in=PaginationIn(offset=0, limit=10),
    )

    assert count == 4
    assert len(list(items)) == 4


@pytest.mark.django_db
def test_create_subject_happy_path(create_use_case):
    created = create_use_case.execute(title="Higher Mathematics")

    assert created.title == "Higher Mathematics"
    assert created.slug is not None


@pytest.mark.django_db
def test_create_subject_already_exists_raises(create_use_case, subject_create):
    existing = subject_create()

    with pytest.raises(SubjectAlreadyExistException):
        create_use_case.execute(title=existing.title)


@pytest.mark.django_db
def test_create_subject_restores_soft_deleted(create_use_case, delete_use_case, subject_create):
    original = subject_create()
    delete_use_case.execute(subject_uuid=str(original.subject_uuid))

    restored = create_use_case.execute(title=original.title)

    assert restored.id == original.id
    assert restored.is_active is True


@pytest.mark.django_db
def test_delete_subject_invalid_uuid_raises(delete_use_case):
    with pytest.raises(InvalidUuidFormatStringException):
        delete_use_case.execute(subject_uuid="bad-uuid")


@pytest.mark.django_db
def test_delete_subject_not_found_raises(delete_use_case):
    with pytest.raises(SubjectNotFoundException):
        delete_use_case.execute(subject_uuid="00000000-0000-0000-0000-000000000000")


@pytest.mark.django_db
def test_delete_subject_used_in_lessons_raises(delete_use_case, subject_create):
    subject = subject_create()
    lesson = LessonModelFactory(subject=subject)
    GroupLessonModelFactory(lesson=lesson)

    with pytest.raises(SubjectIsUsedInLessonsException):
        delete_use_case.execute(subject_uuid=str(subject.subject_uuid))


@pytest.mark.django_db
def test_delete_subject_soft_deletes(delete_use_case, subject_create, subject_service):
    subject = subject_create()

    delete_use_case.execute(subject_uuid=str(subject.subject_uuid))

    found = subject_service.find_any_by_title(title=subject.title)
    assert found is not None
    assert found.is_active is False


@pytest.mark.django_db
def test_update_subject_invalid_uuid_raises(update_use_case):
    with pytest.raises(InvalidUuidFormatStringException):
        update_use_case.execute(subject_uuid="bad", title="New Title")


@pytest.mark.django_db
def test_update_subject_not_found_raises(update_use_case):
    with pytest.raises(SubjectNotFoundException):
        update_use_case.execute(
            subject_uuid="00000000-0000-0000-0000-000000000000",
            title="New Title",
        )


@pytest.mark.django_db
def test_update_subject_already_taken_raises(update_use_case, subject_create_batch):
    s1, s2 = subject_create_batch(size=2)

    with pytest.raises(SubjectAlreadyExistException):
        update_use_case.execute(subject_uuid=str(s1.subject_uuid), title=s2.title)


@pytest.mark.django_db
def test_update_subject_happy_path(update_use_case, subject_create):
    subject = subject_create()

    updated = update_use_case.execute(
        subject_uuid=str(subject.subject_uuid),
        title="Brand New Subject Title",
    )

    assert updated.title == "Brand New Subject Title"
    assert updated.id == subject.id
