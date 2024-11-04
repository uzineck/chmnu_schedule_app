from dataclasses import dataclass
from typing import Any

from core.apps.common.time.constants import START_OF_ACADEMIC_SEMESTER
from core.apps.common.time.entity import TimeInfo as TimeInfoEntity
from core.apps.common.time.service import BaseTimeService


@dataclass
class GetCurrentTimeInfo:
    time_service: BaseTimeService

    def execute(self) -> Any:
        current_time = self.time_service.get_current_time()
        current_week = self.time_service.get_current_week_type(
            datetime_now=current_time,
            start_of_academic_semester=START_OF_ACADEMIC_SEMESTER,
        )
        current_day = self.time_service.get_current_day(datetime_now=current_time)
        current_lesson = self.time_service.get_current_lesson(datetime_now=current_time)
        return TimeInfoEntity(current_week_is_even=current_week, current_day=current_day, current_lesson=current_lesson)
