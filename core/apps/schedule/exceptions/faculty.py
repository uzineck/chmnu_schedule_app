from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class FacultyNotFoundException(ServiceException):
    uuid: str | None = None
    id: int | None = None

    @property
    def message(self):
        return 'Faculty with provided identifier not found'


@dataclass(eq=False)
class FacultyAlreadyExistsException(ServiceException):
    code_name: str | None = None
    name: str | None = None

    @property
    def message(self):
        return 'Faculty with provided parameters already exists'


@dataclass(eq=False)
class FacultyUpdateException(ServiceException):
    id: int

    @property
    def message(self):
        return 'An error occurred while updating faculty'


@dataclass(eq=False)
class FacultyDeleteException(ServiceException):
    id: int

    @property
    def message(self):
        return 'An error occurred while deleting faculty'


@dataclass(eq=False)
class OldAndNewFacultyNamesAreSimilarException(ServiceException):
    old_name: str
    new_name: str

    @property
    def message(self):
        return 'Old faculty name and the new one are similar'


@dataclass(eq=False)
class OldAndNewFacultyCodeNamesAreSimilarException(ServiceException):
    old_code_name: str
    new_code_name: str

    @property
    def message(self):
        return 'Old faculty code name and the new one are similar'
