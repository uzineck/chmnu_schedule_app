import pytest
from django.core.cache import cache
from tests.factories.schedule.group import GroupModelFactory

from core.api.filters import PaginationIn
from core.apps.common.filters import SearchFilter
from core.apps.schedule.exceptions.faculty import (
    FacultyAlreadyExistsException,
    FacultyHasGroupsException,
    FacultyNotFoundException,
)
from core.apps.schedule.exceptions.validators.uuid_validator import InvalidUuidFormatStringException
from core.apps.schedule.use_cases.faculty.create import CreateFacultyUseCase
from core.apps.schedule.use_cases.faculty.delete import DeleteFacultyUseCase
from core.apps.schedule.use_cases.faculty.get_all import GetAllFacultiesUseCase
from core.apps.schedule.use_cases.faculty.get_list import GetFacultyListUseCase
from core.apps.schedule.use_cases.faculty.update_code_name import UpdateFacultyCodeNameUseCase
from core.apps.schedule.use_cases.faculty.update_name import UpdateFacultyNameUseCase


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def get_all_use_case(container) -> GetAllFacultiesUseCase:
    return container.resolve(GetAllFacultiesUseCase)


@pytest.fixture
def get_list_use_case(container) -> GetFacultyListUseCase:
    return container.resolve(GetFacultyListUseCase)


@pytest.fixture
def create_use_case(container) -> CreateFacultyUseCase:
    return container.resolve(CreateFacultyUseCase)


@pytest.fixture
def delete_use_case(container) -> DeleteFacultyUseCase:
    return container.resolve(DeleteFacultyUseCase)


@pytest.fixture
def update_name_use_case(container) -> UpdateFacultyNameUseCase:
    return container.resolve(UpdateFacultyNameUseCase)


@pytest.fixture
def update_code_name_use_case(container) -> UpdateFacultyCodeNameUseCase:
    return container.resolve(UpdateFacultyCodeNameUseCase)


# --- GetAll / GetList ---

@pytest.mark.django_db
def test_get_all_faculties_returns_list(get_all_use_case, faculty_create_batch):
    faculty_create_batch(size=3)

    result = get_all_use_case.execute()

    assert len(result) == 3


@pytest.mark.django_db
def test_get_faculty_list_returns_paginated(get_list_use_case, faculty_create_batch):
    faculty_create_batch(size=5)

    items, count = get_list_use_case.execute(
        filters=SearchFilter(),
        pagination_in=PaginationIn(offset=0, limit=10),
    )

    assert count == 5
    assert len(list(items)) == 5


# --- Create ---

@pytest.mark.django_db
def test_create_faculty_happy_path(create_use_case, faculty_build):
    faculty = faculty_build()

    created = create_use_case.execute(name=faculty.name, code_name=faculty.code_name)

    assert created.name == faculty.name
    assert created.code_name == faculty.code_name


@pytest.mark.django_db
def test_create_faculty_already_exists_by_name_raises(create_use_case, faculty_create, faculty_build):
    existing = faculty_create()
    new_distinct = faculty_build()

    with pytest.raises(FacultyAlreadyExistsException):
        create_use_case.execute(name=existing.name, code_name=new_distinct.code_name)


@pytest.mark.django_db
def test_create_faculty_already_exists_by_code_name_raises(create_use_case, faculty_create, faculty_build):
    existing = faculty_create()
    new_distinct = faculty_build()

    with pytest.raises(FacultyAlreadyExistsException):
        create_use_case.execute(name=new_distinct.name, code_name=existing.code_name)


@pytest.mark.django_db
def test_create_faculty_restores_soft_deleted_match(
        create_use_case,
        delete_use_case,
        faculty_create,
):
    original = faculty_create()
    delete_use_case.execute(faculty_uuid=str(original.faculty_uuid))

    restored = create_use_case.execute(name=original.name, code_name=original.code_name)

    assert restored.id == original.id
    assert restored.is_active is True


# --- Delete ---

@pytest.mark.django_db
def test_delete_faculty_invalid_uuid_raises(delete_use_case):
    with pytest.raises(InvalidUuidFormatStringException):
        delete_use_case.execute(faculty_uuid="not-a-uuid")


@pytest.mark.django_db
def test_delete_faculty_not_found_raises(delete_use_case):
    with pytest.raises(FacultyNotFoundException):
        delete_use_case.execute(faculty_uuid="00000000-0000-0000-0000-000000000000")


@pytest.mark.django_db
def test_delete_faculty_has_groups_raises(delete_use_case, faculty_create):
    faculty = faculty_create()
    GroupModelFactory(faculty=faculty)

    with pytest.raises(FacultyHasGroupsException):
        delete_use_case.execute(faculty_uuid=str(faculty.faculty_uuid))


@pytest.mark.django_db
def test_delete_faculty_soft_deletes(delete_use_case, faculty_create, faculty_service):
    faculty = faculty_create()

    delete_use_case.execute(faculty_uuid=str(faculty.faculty_uuid))

    found = faculty_service.find_any_by_code_name(faculty_code_name=faculty.code_name)
    assert found is not None
    assert found.is_active is False


# --- Update name ---

@pytest.mark.django_db
def test_update_faculty_name_invalid_uuid_raises(update_name_use_case):
    with pytest.raises(InvalidUuidFormatStringException):
        update_name_use_case.execute(faculty_uuid="bad-uuid", name="New Name")


@pytest.mark.django_db
def test_update_faculty_name_not_found_raises(update_name_use_case):
    with pytest.raises(FacultyNotFoundException):
        update_name_use_case.execute(
            faculty_uuid="00000000-0000-0000-0000-000000000000",
            name="New Name",
        )


@pytest.mark.django_db
def test_update_faculty_name_same_as_old_raises_already_exists(update_name_use_case, faculty_create):
    # Note: SimilarOldAndNewFacultyNameValidatorService is dead from this path —
    # AlreadyExistsByNameValidatorService runs first and the current name IS in the DB,
    # so the "already exists" check always fires before "old == new". Asserting actual behavior.
    faculty = faculty_create()

    with pytest.raises(FacultyAlreadyExistsException):
        update_name_use_case.execute(faculty_uuid=str(faculty.faculty_uuid), name=faculty.name)


@pytest.mark.django_db
def test_update_faculty_name_already_taken_raises(update_name_use_case, faculty_create_batch):
    f1, f2 = faculty_create_batch(size=2)

    with pytest.raises(FacultyAlreadyExistsException):
        update_name_use_case.execute(faculty_uuid=str(f1.faculty_uuid), name=f2.name)


@pytest.mark.django_db
def test_update_faculty_name_happy_path(update_name_use_case, faculty_create):
    faculty = faculty_create()

    updated = update_name_use_case.execute(
        faculty_uuid=str(faculty.faculty_uuid),
        name="Brand New Faculty Name",
    )

    assert updated.name == "Brand New Faculty Name"
    assert updated.id == faculty.id


# --- Update code_name ---

@pytest.mark.django_db
def test_update_faculty_code_name_same_as_old_raises_already_exists(update_code_name_use_case, faculty_create):
    # Same dead-path note as test_update_faculty_name_same_as_old_raises_already_exists.
    faculty = faculty_create()

    with pytest.raises(FacultyAlreadyExistsException):
        update_code_name_use_case.execute(
            faculty_uuid=str(faculty.faculty_uuid),
            code_name=faculty.code_name,
        )


@pytest.mark.django_db
def test_update_faculty_code_name_already_taken_raises(
        update_code_name_use_case,
        faculty_create_batch,
):
    f1, f2 = faculty_create_batch(size=2)

    with pytest.raises(FacultyAlreadyExistsException):
        update_code_name_use_case.execute(
            faculty_uuid=str(f1.faculty_uuid),
            code_name=f2.code_name,
        )


@pytest.mark.django_db
def test_update_faculty_code_name_happy_path(update_code_name_use_case, faculty_create):
    faculty = faculty_create()

    updated = update_code_name_use_case.execute(
        faculty_uuid=str(faculty.faculty_uuid),
        code_name="NEW-CODE",
    )

    assert updated.code_name == "NEW-CODE"
    assert updated.id == faculty.id
