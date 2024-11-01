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
        return f'Room with provided number already exists {self.number=}'


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


@dataclass(eq=False)
class OldAndNewRoomsAreSimilarException(ServiceException):
    old_number: str
    new_number: str

    @property
    def message(self):
        return 'Old room number and the new one are similar'


@dataclass(eq=False)
class OldAndNewRoomDescriptionsAreSimilarException(ServiceException):
    old_description: str
    new_description: str

    @property
    def message(self):
        return 'Old room description and the new one are similar'
