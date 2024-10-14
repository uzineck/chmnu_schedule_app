from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class RoomNotFoundException(ServiceException):
    uuid: str | None = None
    id: int | None = None
    number: str | None = None

    @property
    def message(self):
        return 'Room with provided identifier not found'


@dataclass(eq=False)
class RoomAlreadyExistException(ServiceException):
    number: str

    @property
    def message(self):
        return 'Room with provided number already exists'


@dataclass(eq=False)
class RoomUpdateException(ServiceException):
    id: int

    @property
    def message(self):
        return 'An error occurred while updating room'


@dataclass(eq=False)
class RoomDeleteException(ServiceException):
    id: int

    @property
    def message(self):
        return 'An error occurred while deleting room'
