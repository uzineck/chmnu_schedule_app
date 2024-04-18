from abc import ABC, abstractmethod

from core.apps.schedule.models import Timeslot as TimeslotModel
from core.apps.schedule.entities.timeslot import Timeslot as TimeslotEntity


class BaseTimeslotService(ABC):
    @abstractmethod
    def get_or_create(self, day: str, ord_number: int, is_even: bool) -> TimeslotEntity:
        ...


class ORMTimeslotService(BaseTimeslotService):
    def get_or_create(self, day: str, ord_number: int, is_even: bool) -> TimeslotEntity:
        timeslot, _ = TimeslotModel.objects.get_or_create(day=day, ord_number=ord_number, is_even=is_even)
        return timeslot.to_entity()
