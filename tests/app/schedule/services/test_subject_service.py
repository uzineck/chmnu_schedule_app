import pytest
from tests.factories.schedule.subject import SubjectModelFactory

from core.api.filters import PaginationIn
from core.apps.common.filters import SearchFilter
from core.apps.schedule.exceptions.subject import (
    SubjectAlreadyExistException,
    SubjectDeleteException,
    SubjectNotFoundException,
    SubjectUpdateException,
)
from core.apps.schedule.services.subject import BaseSubjectService


@pytest.mark.django_db
def test_create_subject_success(subject_service: BaseSubjectService):
    subject = SubjectModelFactory.build()
    created_subject = subject_service.create(
        title=subject.title,
        slug=subject.slug,
    )

    assert created_subject.title == subject.title
    assert created_subject.slug == subject.slug


@pytest.mark.django_db
def test_create_subject_already_exists_failure(subject_service: BaseSubjectService):
    subject = SubjectModelFactory.create()

    with pytest.raises(SubjectAlreadyExistException):
        subject_service.create(
            title=subject.title,
            slug=subject.slug,
        )


@pytest.mark.django_db
def test_get_count_subject_zero(subject_service: BaseSubjectService):
    subject_count = subject_service.get_count(filters=SearchFilter())
    assert subject_count == 0, f"{subject_count=}"


@pytest.mark.django_db
def test_get_count_subject_exist(subject_service: BaseSubjectService):
    expected_count = 5
    SubjectModelFactory.create_batch(size=expected_count)

    subject_count = subject_service.get_count(filters=SearchFilter())
    assert subject_count == expected_count, f"{subject_count=}"


@pytest.mark.django_db
def test_get_all_subjects_success(subject_service: BaseSubjectService):
    expected_count = 5
    subjects = SubjectModelFactory.create_batch(size=expected_count)
    subject_titles = {subject.title for subject in subjects}

    fetched_subjects = subject_service.get_all()
    fetched_titles = {subject.title for subject in fetched_subjects}

    assert len(fetched_titles) == expected_count, f"{fetched_titles=}"
    assert subject_titles == fetched_titles, f"{subject_titles=}"


@pytest.mark.django_db
def test_get_list_subject_success(subject_service: BaseSubjectService):
    expected_count = 5
    subjects = SubjectModelFactory.create_batch(size=expected_count)
    subject_titles = {subject.title for subject in subjects}

    fetched_subjects = subject_service.get_list(filters=SearchFilter(), pagination=PaginationIn())
    fetched_titles = {subject.title for subject in fetched_subjects}

    assert len(fetched_titles) == expected_count, f"{fetched_titles=}"
    assert subject_titles == fetched_titles, f"{subject_titles=}"


@pytest.mark.django_db
def test_get_by_uuid_subject_success(subject_service: BaseSubjectService):
    subject = SubjectModelFactory.create()

    found_subject = subject_service.get_by_uuid(subject_uuid=subject.subject_uuid)

    assert subject.subject_uuid == found_subject.uuid
    assert subject.title == found_subject.title
    assert subject.slug == found_subject.slug


@pytest.mark.django_db
def test_get_by_uuid_subject_not_found_failure(subject_service: BaseSubjectService):
    subject = SubjectModelFactory.build()

    with pytest.raises(SubjectNotFoundException):
        subject_service.get_by_uuid(subject_uuid=subject.subject_uuid)


@pytest.mark.django_db
def test_get_by_id_subject_success(subject_service: BaseSubjectService):
    subject = SubjectModelFactory.create()

    found_subject = subject_service.get_by_id(subject_id=subject.id)

    assert subject.id == found_subject.id
    assert subject.title == found_subject.title
    assert subject.slug == found_subject.slug


@pytest.mark.django_db
def test_get_by_id_subject_not_found_failure(subject_service: BaseSubjectService):
    subject = SubjectModelFactory.build()

    with pytest.raises(SubjectNotFoundException):
        subject_service.get_by_id(subject_id=subject.id)


@pytest.mark.django_db
def test_check_exists_by_title_subject_true(subject_service: BaseSubjectService):
    subject = SubjectModelFactory.create()

    assert subject_service.check_exists_by_title(title=subject.title) is True


@pytest.mark.django_db
def test_check_exists_by_title_subject_false(subject_service: BaseSubjectService):
    subject = SubjectModelFactory.build()

    assert subject_service.check_exists_by_title(title=subject.title) is False


@pytest.mark.django_db
def test_update_subject_success(subject_service: BaseSubjectService):
    subject = SubjectModelFactory.create()

    new_subject = SubjectModelFactory.build()

    assert subject_service.update(subject_id=subject.id, title=new_subject.title, slug=new_subject.slug) is None


@pytest.mark.django_db
def test_update_subject_failure(subject_service: BaseSubjectService):
    subject = SubjectModelFactory.build()

    with pytest.raises(SubjectUpdateException):
        subject_service.update(subject_id=subject.id, title=subject.title, slug=subject.slug)


@pytest.mark.django_db
def test_delete_subject_success(subject_service: BaseSubjectService):
    subject = SubjectModelFactory.create()

    assert subject_service.delete(subject_id=subject.id) is None


@pytest.mark.django_db
def test_delete_subject_failure(subject_service: BaseSubjectService):
    subject = SubjectModelFactory.build()

    with pytest.raises(SubjectDeleteException):
        subject_service.delete(subject_id=subject.id)
