from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class LessonNotFoundException(ServiceException):
    lesson_id: int

    @property
    def message(self):
        return 'Lesson with provided id not found'
