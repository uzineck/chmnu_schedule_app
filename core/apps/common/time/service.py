import pytz
from abc import (
    ABC,
    abstractmethod,
)
from datetime import (
    datetime,
    time,
)

from core.apps.common.models import OrdinaryNumber


class BaseTimeService(ABC):
    @abstractmethod
    def get_current_time(self) -> datetime:
        ...

    @abstractmethod
    def get_current_week_type(
            self,
            datetime_now: datetime,
            start_of_academic_semester: datetime,
            start_of_academic_semester_line: bool,
    ) -> bool:
        ...

    @abstractmethod
    def get_current_day(self, datetime_now: datetime) -> int:
        ...

    @abstractmethod
    def get_current_lesson(
            self,
            datetime_now: datetime,
            lesson_timetable: dict[OrdinaryNumber, tuple[time, time]],
            start_of_academic_day: time,
            end_of_academic_day: time,
    ) -> int:
        ...


class DatetimeTimeService(BaseTimeService):
    def get_current_time(self) -> datetime:
        current_time = datetime.now(tz=pytz.timezone('Europe/Kyiv'))
        return current_time

    def get_current_week_type(
            self,
            datetime_now: datetime,
            start_of_academic_semester: datetime,
            start_of_academic_semester_line: bool,  # At the start of academic semester the line
                                                    # is above(True) or below(False)
    ) -> bool:
        weeks_since_start = (datetime_now.date() - start_of_academic_semester.date()).days // 7
        # Every even week will be True, every odd week will be False
        # The first week is when weeks_since_start = 0
        if (weeks_since_start % 2 == 0) == start_of_academic_semester_line:
            return True  # Returns True if the week is above the line
        else:
            return False  # Returns False if the week is below the line

    def get_current_day(self, datetime_now: datetime) -> int:
        current_day = datetime_now.isoweekday()
        return current_day

    def get_current_lesson(
            self,
            datetime_now: datetime,
            lesson_timetable: dict[OrdinaryNumber, tuple[time, time]],
            start_of_academic_day: time,
            end_of_academic_day: time,
    ) -> int:
        current_time = datetime_now.time()

        # Lesson time
        for lesson_number, (start_time, end_time) in lesson_timetable.items():
            if start_time <= current_time <= end_time:
                return lesson_number  # Can be pydantic error(change to lesson_number.value)

        # Break time
        if start_of_academic_day <= current_time <= end_of_academic_day:
            return 0

        # Out of working time
        return -1
