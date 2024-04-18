from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class RoomNotFoundException(ServiceException):
    number: str

    @property
    def message(self):
        return 'Room with provided number not found'


@dataclass(eq=False)
class RoomAlreadyExistException(ServiceException):
    number: str

    @property
    def message(self):
        return 'Room with provided number already exists'

