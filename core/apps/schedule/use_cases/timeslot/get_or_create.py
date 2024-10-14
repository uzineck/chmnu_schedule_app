from dataclasses import dataclass

from core.apps.common.models import (
    Day,
    OrdinaryNumber,
)
from core.apps.schedule.entities.timeslot import Timeslot as TimeslotEntity
from core.apps.schedule.services.timeslot import BaseTimeslotService


@dataclass
class CreateTimeslotUseCase:
    timeslot_service: BaseTimeslotService

    def execute(self, day: Day, ord_number: OrdinaryNumber, is_even: bool) -> TimeslotEntity:
        timeslot = self.timeslot_service.get_or_create(day=day, ord_number=ord_number, is_even=is_even)

        return timeslot
