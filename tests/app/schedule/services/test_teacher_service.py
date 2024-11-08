import pytest

from core.api.filters import PaginationIn
from core.apps.schedule.exceptions.teacher import (
    TeacherNotFoundException,
    TeacherUpdateException,
)
from core.apps.schedule.filters.teacher import TeacherFilter
from core.apps.schedule.services.teacher import BaseTeacherService


@pytest.mark.django_db
def test_create_teacher_success(teacher_service: BaseTeacherService, teacher_build):
    teacher = teacher_build()

    created_teacher = teacher_service.create(
        first_name=teacher.first_name,
        last_name=teacher.last_name,
        middle_name=teacher.middle_name,
        rank=teacher.rank,
    )

    assert created_teacher.first_name == teacher.first_name
    assert created_teacher.last_name == teacher.last_name
    assert created_teacher.middle_name == teacher.middle_name
    assert created_teacher.rank == teacher.rank


# @pytest.mark.django_db
# def test_create_teacher_already_exists_failure(teacher_service: BaseTeacherService, teacher_create):
#     teacher = teacher_create()
#
#     with pytest.raises(TeacherAlreadyExistsException):
#         teacher_service.create(
#             first_name=teacher.first_name,
#             last_name=teacher.last_name,
#             middle_name=teacher.middle_name,
#             rank=teacher.rank,
#         )


@pytest.mark.django_db
def test_get_count_teacher_zero(teacher_service: BaseTeacherService):
    teacher_count = teacher_service.get_count(filters=TeacherFilter())
    assert teacher_count == 0, f"{teacher_count=}"


@pytest.mark.django_db
def test_get_count_teacher_exist(teacher_service: BaseTeacherService, teacher_create_batch):
    expected_count = 5
    teacher_create_batch(size=expected_count)

    teacher_count = teacher_service.get_count(filters=TeacherFilter())
    assert teacher_count == expected_count, f"{teacher_count=}"


@pytest.mark.django_db
def test_get_all_teachers_success(teacher_service: BaseTeacherService, teacher_create_batch):
    expected_count = 5
    teachers = teacher_create_batch(size=expected_count)
    teacher_last_names = {teacher.last_name for teacher in teachers}

    fetched_teacher = teacher_service.get_all()
    fetched_last_names = {teacher.last_name for teacher in fetched_teacher}

    assert len(fetched_last_names) == expected_count, f"{fetched_last_names=}"
    assert teacher_last_names == fetched_last_names, f"{teacher_last_names=}"


@pytest.mark.django_db
def test_get_list_teachers_success(teacher_service: BaseTeacherService, teacher_create_batch):
    expected_count = 5
    teachers = teacher_create_batch(size=expected_count)
    teacher_last_names = {teacher.last_name for teacher in teachers}

    fetched_teacher = teacher_service.get_list(filters=TeacherFilter(), pagination=PaginationIn())
    fetched_last_names = {teacher.last_name for teacher in fetched_teacher}

    assert len(fetched_last_names) == expected_count, f"{fetched_last_names=}"
    assert teacher_last_names == fetched_last_names, f"{teacher_last_names=}"


@pytest.mark.django_db
def test_get_by_uuid_teacher_success(teacher_service: BaseTeacherService, teacher_create):
    teacher = teacher_create()

    found_teacher = teacher_service.get_by_uuid(teacher_uuid=teacher.teacher_uuid)

    assert teacher.teacher_uuid == found_teacher.uuid
    assert teacher.first_name == found_teacher.first_name


@pytest.mark.django_db
def test_get_by_uuid_teacher_not_found_failure(teacher_service: BaseTeacherService, teacher_build):
    teacher = teacher_build()

    with pytest.raises(TeacherNotFoundException):
        teacher_service.get_by_uuid(teacher_uuid=teacher.teacher_uuid)


@pytest.mark.django_db
def test_get_by_id_teacher_success(teacher_service: BaseTeacherService, teacher_create):
    teacher = teacher_create()

    found_teacher = teacher_service.get_by_id(teacher_id=teacher.id)

    assert teacher.id == found_teacher.id
    assert teacher.first_name == found_teacher.first_name


@pytest.mark.django_db
def test_get_by_id_teacher_not_found_failure(teacher_service: BaseTeacherService, teacher_build):
    teacher = teacher_build()

    with pytest.raises(TeacherNotFoundException):
        teacher_service.get_by_id(teacher_id=teacher.id)


@pytest.mark.django_db
def test_check_exists_by_full_name_teacher_true(teacher_service: BaseTeacherService, teacher_create):
    teacher = teacher_create()

    assert teacher_service.check_exists_by_full_name(
        first_name=teacher.first_name,
        last_name=teacher.last_name,
        middle_name=teacher.middle_name,
    ) is True


@pytest.mark.django_db
def test_check_exists_by_full_name_teacher_false(teacher_service: BaseTeacherService, teacher_build):
    teacher = teacher_build()

    assert teacher_service.check_exists_by_full_name(
        first_name=teacher.first_name,
        last_name=teacher.last_name,
        middle_name=teacher.middle_name,
    ) is False


@pytest.mark.django_db
def test_update_name_teacher_success(teacher_service: BaseTeacherService, teacher_create, teacher_build):
    teacher = teacher_create()
    new_teacher = teacher_build()

    assert teacher_service.update_name(
        teacher_id=teacher.id,
        first_name=new_teacher.first_name,
        last_name=new_teacher.last_name,
        middle_name=new_teacher.middle_name,
    ) is None


@pytest.mark.django_db
def test_update_name_teacher_failure(teacher_service: BaseTeacherService, teacher_build):
    teacher = teacher_build()

    with pytest.raises(TeacherUpdateException):
        teacher_service.update_name(
            teacher_id=teacher.id,
            first_name=teacher.first_name,
            last_name=teacher.last_name,
            middle_name=teacher.middle_name,
        )


@pytest.mark.django_db
def test_update_rank_teacher_success(teacher_service: BaseTeacherService, teacher_create, teacher_build):
    teacher = teacher_create()
    new_teacher = teacher_build()

    assert teacher_service.update_rank(
        teacher_id=teacher.id,
        rank=new_teacher.rank,
    ) is None


@pytest.mark.django_db
def test_update_rank_teacher_failure(teacher_service: BaseTeacherService, teacher_build):
    teacher = teacher_build()

    with pytest.raises(TeacherUpdateException):
        teacher_service.update_rank(
            teacher_id=teacher.id,
            rank=teacher.rank,
        )


@pytest.mark.django_db
def test_update_is_active_teacher_success(teacher_service: BaseTeacherService, teacher_create):
    teacher = teacher_create()

    assert teacher_service.update_is_active(
        teacher_id=teacher.id,
    ) is None


@pytest.mark.django_db
def test_update_is_active_teacher_failure(teacher_service: BaseTeacherService, teacher_build):
    teacher = teacher_build()

    with pytest.raises(TeacherUpdateException):
        teacher_service.update_is_active(
            teacher_id=teacher.id,
        )
