from dataclasses import dataclass
from datetime import (
    datetime,
    time,
)

from core.apps.common.time.constants import (
    END_OF_ACADEMIC_DAY,
    LESSON_TIMETABLE,
    START_OF_ACADEMIC_DAY,
)
from core.apps.common.time.entity import TimeInfo as TimeInfoEntity
from core.apps.common.time.service import BaseTimeService
from core.apps.schedule.services.semester_settings import BaseSemesterSettingsService


@dataclass
class GetCurrentTimeInfoUseCase:
    time_service: BaseTimeService
    semester_settings_service: BaseSemesterSettingsService

    def execute(self) -> TimeInfoEntity:
        current_time = self.time_service.get_current_time()
        semester_settings = self.semester_settings_service.get_current_settings()
        start_of_semester = datetime.combine(semester_settings.start_date, time.min)
        current_week = self.time_service.get_current_week_type(
            datetime_now=current_time,
            start_of_academic_semester=start_of_semester,
            start_of_academic_semester_line=semester_settings.is_above_line,
        )
        current_day = self.time_service.get_current_day(datetime_now=current_time)
        current_lesson = self.time_service.get_current_lesson(
            datetime_now=current_time,
            lesson_timetable=LESSON_TIMETABLE,
            start_of_academic_day=START_OF_ACADEMIC_DAY,
            end_of_academic_day=END_OF_ACADEMIC_DAY,
        )
        return TimeInfoEntity(
            current_week_is_even=current_week,
            current_day=current_day,
            current_lesson=current_lesson,
        )
