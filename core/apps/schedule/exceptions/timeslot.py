from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class TimeslotNotFoundException(ServiceException):
    timeslot_id: int

    @property
    def message(self):
        return 'Timeslot with provided id not found'
