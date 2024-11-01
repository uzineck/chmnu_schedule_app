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


@dataclass(eq=False)
class OldAndNewTeacherNamesAreSimilarException(ServiceException):
    first_name: str
    last_name: str
    middle_name: str
    old_first_name: str
    old_last_name: str
    old_middle_name: str

    @property
    def message(self):
        return 'Old teacher name and the new one are similar'


@dataclass(eq=False)
class OldAndNewTeacherRanksAreSimilarException(ServiceException):
    old_rank: str
    new_rank: str

    @property
    def message(self):
        return 'Old teacher rank and the new one are similar'
