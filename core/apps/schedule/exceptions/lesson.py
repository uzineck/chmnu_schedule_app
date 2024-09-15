from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class LessonNotFoundException(ServiceException):
    uuid: str

    @property
    def message(self):
        return f'Lesson with provided uuid not found ({self.uuid})'
