from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class TeacherNotFoundException(ServiceException):
    id: int

    @property
    def message(self):
        return 'Teacher with provided id not found'

