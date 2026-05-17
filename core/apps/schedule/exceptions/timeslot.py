from dataclasses import dataclass

from core.apps.common.exceptions import NotFoundException


@dataclass(eq=False)
class TimeslotNotFoundException(NotFoundException):
    timeslot_id: int

    @property
    def message(self):
        return 'Timeslot with provided id was not found'
