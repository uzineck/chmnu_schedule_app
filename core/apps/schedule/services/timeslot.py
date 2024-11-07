import logging
from abc import (
    ABC,
    abstractmethod,
)

from core.apps.common.models import (
    Day,
    OrdinaryNumber,
)
from core.apps.schedule.entities.timeslot import Timeslot as TimeslotEntity
from core.apps.schedule.exceptions.timeslot import TimeslotNotFoundException
from core.apps.schedule.models import Timeslot as TimeslotModel


logger = logging.getLogger(__name__)


class BaseTimeslotService(ABC):
    @abstractmethod
    def get_or_create(self, day: Day, ord_number: OrdinaryNumber, is_even: bool) -> TimeslotEntity:
        ...

    @abstractmethod
    def get_by_id(self, timeslot_id: int) -> TimeslotEntity:
        ...


class ORMTimeslotService(BaseTimeslotService):
    def get_or_create(self, day: Day, ord_number: OrdinaryNumber, is_even: bool) -> TimeslotEntity:
        timeslot, _ = TimeslotModel.objects.get_or_create(day=day, ord_number=ord_number, is_even=is_even)
        return timeslot.to_entity()

    def get_by_id(self, timeslot_id: int) -> TimeslotEntity:
        try:
            timeslot = TimeslotModel.objects.get(id=timeslot_id)
        except TimeslotModel.DoesNotExist:
            logger.error(f"Timeslot Does Not Exist Error ({timeslot_id=})")
            raise TimeslotNotFoundException(timeslot_id=timeslot_id)

        return timeslot.to_entity()
