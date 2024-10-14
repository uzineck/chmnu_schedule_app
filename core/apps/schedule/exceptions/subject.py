from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class SubjectNotFoundException(ServiceException):
    uuid: str | None = None
    id: int | None = None

    @property
    def message(self):
        return 'Subject with provided identifier not found'


@dataclass(eq=False)
class SubjectAlreadyExistException(ServiceException):
    title: str

    @property
    def message(self):
        return 'Subject with provided title already exists'


@dataclass(eq=False)
class SubjectUpdateException(ServiceException):
    id: int

    @property
    def message(self):
        return 'An error occurred while updating subject'


@dataclass(eq=False)
class SubjectDeleteException(ServiceException):
    id: int

    @property
    def message(self):
        return 'An error occurred while deleting subject'
