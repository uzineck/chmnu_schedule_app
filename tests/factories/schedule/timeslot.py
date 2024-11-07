import factory
from factory.django import DjangoModelFactory

from core.apps.common.models import (
    Day,
    OrdinaryNumber,
)
from core.apps.schedule.models import Timeslot


class TimeslotModelFactory(DjangoModelFactory):
    id = factory.Sequence(lambda n: n)
    day = factory.Iterator(Day)
    ord_number = factory.Iterator(OrdinaryNumber)
    is_even = factory.Iterator([True, False])

    class Meta:
        model = Timeslot
