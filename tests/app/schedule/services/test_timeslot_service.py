import pytest

from core.apps.schedule.exceptions.timeslot import TimeslotNotFoundException
from core.apps.schedule.services.timeslot import BaseTimeslotService


@pytest.mark.django_db
def test_get_or_create_create_timeslot_success(timeslot_service: BaseTimeslotService, timeslot_build):
    timeslot = timeslot_build()

    created_timeslot = timeslot_service.get_or_create(
        day=timeslot.day,
        ord_number=timeslot.ord_number,
        is_even=timeslot.is_even,
    )

    assert created_timeslot.day == timeslot.day
    assert created_timeslot.ord_number == timeslot.ord_number
    assert created_timeslot.is_even == timeslot.is_even


@pytest.mark.django_db
def test_get_or_create_get_timeslot_success(timeslot_service: BaseTimeslotService, timeslot_create):
    timeslot = timeslot_create()

    found_timeslot = timeslot_service.get_or_create(
        day=timeslot.day,
        ord_number=timeslot.ord_number,
        is_even=timeslot.is_even,
    )

    assert found_timeslot.day == timeslot.day
    assert found_timeslot.ord_number == timeslot.ord_number
    assert found_timeslot.is_even == timeslot.is_even


@pytest.mark.django_db
def test_get_by_id_timeslot_success(timeslot_service: BaseTimeslotService, timeslot_create):
    timeslot = timeslot_create()

    found_timeslot = timeslot_service.get_by_id(timeslot_id=timeslot.id)

    assert timeslot.id == found_timeslot.id
    assert found_timeslot.day == timeslot.day
    assert found_timeslot.ord_number == timeslot.ord_number
    assert found_timeslot.is_even == timeslot.is_even


@pytest.mark.django_db
def test_get_by_id_timeslot_not_found_failure(timeslot_service: BaseTimeslotService, timeslot_build):
    timeslot = timeslot_build()

    with pytest.raises(TimeslotNotFoundException):
        timeslot_service.get_by_id(timeslot_id=timeslot.id)
