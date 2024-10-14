from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class TeacherNotFoundException(ServiceException):
    uuid: str | None = None
    id: int | None = None

    @property
    def message(self):
        return 'Teacher with provided identifier not found'


@dataclass(eq=False)
class TeacherAlreadyExistsException(ServiceException):
    first_name: str
    last_name: str
    middle_name: str

    @property
    def message(self):
        return 'Teacher with provided parameters already exists'


@dataclass(eq=False)
class TeacherUpdateException(ServiceException):
    id: int

    @property
    def message(self):
        return 'An error occurred while updating teacher'
