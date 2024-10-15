from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class LessonNotFoundException(ServiceException):
    uuid: str | None = None
    id: str | None = None

    @property
    def message(self):
        return 'Lesson with provided identifier not found'
