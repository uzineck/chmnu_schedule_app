from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class TeacherNotFoundException(ServiceException):
    uuid: str

    @property
    def message(self):
        return 'Teacher with provided uuid not found'

