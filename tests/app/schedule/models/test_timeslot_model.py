from django.db import IntegrityError

import pytest
from tests.factories.schedule.timeslot import TimeslotModelFactory

from core.apps.common.models import (
    Day,
    OrdinaryNumber,
)
from core.apps.schedule.entities.timeslot import Timeslot as TimeslotEntity
from core.apps.schedule.models import Timeslot


@pytest.mark.django_db
def test_timeslot_create():
    timeslot = TimeslotModelFactory.create(
        day=Day.MONDAY,
        ord_number=OrdinaryNumber.FIRST,
        is_even=True,
    )

    assert timeslot.pk is not None
    assert timeslot.day == Day.MONDAY
    assert timeslot.ord_number == OrdinaryNumber.FIRST
    assert timeslot.is_even is True
    assert timeslot.created_at is not None
    assert timeslot.updated_at is not None


@pytest.mark.django_db
def test_timeslot_unique_together_constraint():
    TimeslotModelFactory.create(day=Day.MONDAY, ord_number=OrdinaryNumber.FIRST, is_even=True)

    with pytest.raises(IntegrityError):
        TimeslotModelFactory.create(day=Day.MONDAY, ord_number=OrdinaryNumber.FIRST, is_even=True)


@pytest.mark.django_db
def test_timeslot_same_day_and_number_different_parity_allowed():
    TimeslotModelFactory.create(day=Day.MONDAY, ord_number=OrdinaryNumber.FIRST, is_even=True)
    ts2 = TimeslotModelFactory.create(day=Day.MONDAY, ord_number=OrdinaryNumber.FIRST, is_even=False)

    assert ts2.pk is not None


@pytest.mark.django_db
def test_timeslot_to_entity_maps_all_fields():
    timeslot = TimeslotModelFactory.create(
        day=Day.FRIDAY,
        ord_number=OrdinaryNumber.THIRD,
        is_even=False,
    )

    entity = timeslot.to_entity()

    assert isinstance(entity, TimeslotEntity)
    assert entity.id == timeslot.id
    assert entity.day == Day.FRIDAY
    assert entity.ord_number == OrdinaryNumber.THIRD
    assert entity.is_even is False
    assert entity.created_at == timeslot.created_at
    assert entity.updated_at == timeslot.updated_at


@pytest.mark.django_db
def test_timeslot_default_ordering():
    TimeslotModelFactory.create(day=Day.WEDNESDAY, ord_number=OrdinaryNumber.SECOND, is_even=True)
    TimeslotModelFactory.create(day=Day.MONDAY, ord_number=OrdinaryNumber.FIRST, is_even=True)
    TimeslotModelFactory.create(day=Day.MONDAY, ord_number=OrdinaryNumber.FIRST, is_even=False)

    timeslots = list(Timeslot.objects.all())

    assert timeslots[0].day == Day.MONDAY
    assert timeslots[1].day == Day.MONDAY
    assert timeslots[2].day == Day.WEDNESDAY


def test_timeslot_str():
    timeslot = TimeslotModelFactory.build(
        day=Day.TUESDAY,
        ord_number=OrdinaryNumber.SECOND,
        is_even=True,
    )

    assert str(timeslot) == f"{Day.TUESDAY} | {OrdinaryNumber.SECOND} | True"
