from datetime import time

from core.apps.common.models import OrdinaryNumber


LESSON_TIMETABLE = {
    OrdinaryNumber.FIRST: (time(9, 0), time(10, 20)),
    OrdinaryNumber.SECOND: (time(10, 30), time(11, 50)),
    OrdinaryNumber.THIRD: (time(12, 30), time(13, 50)),
    OrdinaryNumber.FOURTH: (time(14, 0), time(15, 20)),
    OrdinaryNumber.FIFTH: (time(15, 30), time(16, 50)),
    OrdinaryNumber.SIXTH: (time(17, 0), time(18, 20)),
}

START_OF_ACADEMIC_DAY = time(9, 0)  # Start of the first lesson
END_OF_ACADEMIC_DAY = time(18, 20)  # End of the last lesson
