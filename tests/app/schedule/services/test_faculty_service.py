import pytest
from tests.factories.schedule.faculty import FacultyModelFactory

from core.api.filters import PaginationIn
from core.apps.common.filters import SearchFilter
from core.apps.schedule.exceptions.faculty import (
    FacultyAlreadyExistsException,
    FacultyDeleteException,
    FacultyNotFoundException,
    FacultyUpdateException,
)
from core.apps.schedule.services.faculty import BaseFacultyService


@pytest.mark.django_db
def test_create_faculty_success(faculty_service: BaseFacultyService):
    faculty = FacultyModelFactory.build()

    created_faculty = faculty_service.create(name=faculty.name, code_name=faculty.code_name)

    assert created_faculty.name == faculty.name
    assert created_faculty.code_name == faculty.code_name


@pytest.mark.django_db
def test_create_faculty_already_exists_failure(faculty_service: BaseFacultyService):
    faculty = FacultyModelFactory.create()

    with pytest.raises(FacultyAlreadyExistsException):
        faculty_service.create(name=faculty.name, code_name=faculty.code_name)


@pytest.mark.django_db
def test_get_count_faculty_zero(faculty_service: BaseFacultyService):
    faculty_count = faculty_service.get_count(filters=SearchFilter())
    assert faculty_count == 0, f"{faculty_count=}"


@pytest.mark.django_db
def test_get_count_faculty_exist(faculty_service: BaseFacultyService):
    expected_count = 5
    faculties = FacultyModelFactory.create_batch(size=expected_count)
    faculty_names = {faculty.name for faculty in faculties}
    faculty_code_names = {faculty.code_name for faculty in faculties}

    faculty_count = faculty_service.get_count(filters=SearchFilter())
    assert len(faculty_names) == expected_count, f"{faculty_names=}"
    assert len(faculty_code_names) == expected_count, f"{faculty_code_names=}"
    assert faculty_count == expected_count, f"{faculty_count=}"


@pytest.mark.django_db
def test_get_all_faculties_success(faculty_service: BaseFacultyService):
    expected_count = 5
    faculties = FacultyModelFactory.create_batch(size=expected_count)
    faculty_names = {faculty.name for faculty in faculties}

    fetched_faculty = faculty_service.get_all()
    fetched_names = {faculty.name for faculty in fetched_faculty}

    assert len(fetched_names) == expected_count, f"{fetched_names=}"
    assert faculty_names == fetched_names, f"{faculty_names=}"


@pytest.mark.django_db
def test_get_list_faculties_success(faculty_service: BaseFacultyService):
    expected_count = 5
    faculties = FacultyModelFactory.create_batch(size=expected_count)
    faculty_names = {faculty.name for faculty in faculties}

    fetched_faculty = faculty_service.get_list(filters=SearchFilter(), pagination=PaginationIn())
    fetched_names = {faculty.name for faculty in fetched_faculty}

    assert len(fetched_names) == expected_count, f"{fetched_names=}"
    assert faculty_names == fetched_names, f"{faculty_names=}"


@pytest.mark.django_db
def test_get_by_uuid_faculty_success(faculty_service: BaseFacultyService):
    faculty = FacultyModelFactory.create()

    found_faculty = faculty_service.get_by_uuid(faculty_uuid=faculty.faculty_uuid)

    assert faculty.faculty_uuid == found_faculty.uuid
    assert faculty.code_name == found_faculty.code_name


@pytest.mark.django_db
def test_get_by_uuid_faculty_not_found_failure(faculty_service: BaseFacultyService):
    faculty = FacultyModelFactory.build()

    with pytest.raises(FacultyNotFoundException):
        faculty_service.get_by_uuid(faculty_uuid=faculty.faculty_uuid)


@pytest.mark.django_db
def test_get_by_id_faculty_success(faculty_service: BaseFacultyService):
    faculty = FacultyModelFactory.create()

    found_faculty = faculty_service.get_by_id(faculty_id=faculty.id)

    assert faculty.id == found_faculty.id
    assert faculty.code_name == found_faculty.code_name


@pytest.mark.django_db
def test_get_by_id_faculty_not_found_failure(faculty_service: BaseFacultyService):
    faculty = FacultyModelFactory.build()

    with pytest.raises(FacultyNotFoundException):
        faculty_service.get_by_id(faculty_id=faculty.id)


@pytest.mark.django_db
def test_check_exists_by_name_faculty_true(faculty_service: BaseFacultyService):
    faculty = FacultyModelFactory.create()

    assert faculty_service.check_exists_by_name(faculty_name=faculty.name) is True


@pytest.mark.django_db
def test_check_exists_by_name_faculty_false(faculty_service: BaseFacultyService):
    faculty = FacultyModelFactory.build()

    assert faculty_service.check_exists_by_name(faculty_name=faculty.name) is False


@pytest.mark.django_db
def test_check_exists_by_code_name_faculty_true(faculty_service: BaseFacultyService):
    faculty = FacultyModelFactory.create()

    assert faculty_service.check_exists_by_code_name(faculty_code_name=faculty.code_name) is True


@pytest.mark.django_db
def test_check_exists_by_code_name_faculty_false(faculty_service: BaseFacultyService):
    faculty = FacultyModelFactory.build()

    assert faculty_service.check_exists_by_code_name(faculty_code_name=faculty.code_name) is False


@pytest.mark.django_db
def test_update_name_faculty_success(faculty_service: BaseFacultyService):
    faculty = FacultyModelFactory.create()
    new_faculty = FacultyModelFactory.build()

    assert faculty_service.update_name(faculty_id=faculty.id, new_name=new_faculty.name) is None


@pytest.mark.django_db
def test_update_name_faculty_failure(faculty_service: BaseFacultyService):
    faculty = FacultyModelFactory.build()

    with pytest.raises(FacultyUpdateException):
        faculty_service.update_name(faculty_id=faculty.id, new_name=faculty.name)


@pytest.mark.django_db
def test_update_code_name_faculty_success(faculty_service: BaseFacultyService):
    faculty = FacultyModelFactory.create()
    new_faculty = FacultyModelFactory.build()

    assert faculty_service.update_code_name(faculty_id=faculty.id, new_code_name=new_faculty.code_name) is None


@pytest.mark.django_db
def test_update_code_name_faculty_failure(faculty_service: BaseFacultyService):
    faculty = FacultyModelFactory.build()

    with pytest.raises(FacultyUpdateException):
        faculty_service.update_code_name(faculty_id=faculty.id, new_code_name=faculty.code_name)


@pytest.mark.django_db
def test_delete_faculty_success(faculty_service: BaseFacultyService):
    faculty = FacultyModelFactory.create()

    assert faculty_service.delete(faculty_id=faculty.id) is None


@pytest.mark.django_db
def test_delete_faculty_failure(faculty_service: BaseFacultyService):
    faculty = FacultyModelFactory.build()

    with pytest.raises(FacultyDeleteException):
        faculty_service.delete(faculty_id=faculty.id)
