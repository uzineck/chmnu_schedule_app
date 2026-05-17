from dataclasses import dataclass

from core.apps.common.exceptions import (
    AlreadyExistsException,
    InUseException,
    NotFoundException,
    UpdateConflictException,
    ValidationException,
)


@dataclass(eq=False)
class RoomNotFoundException(NotFoundException):
    uuid: str | None = None
    id: int | None = None
    number: str | None = None

    @property
    def message(self):
        return 'Room with given identifier was not found'


@dataclass(eq=False)
class RoomAlreadyExistException(AlreadyExistsException):
    number: str

    @property
    def message(self):
        return 'Room with given number already exists'


@dataclass(eq=False)
class RoomUpdateException(UpdateConflictException):
    id: int

    @property
    def message(self):
        return 'Failed to update room'


@dataclass(eq=False)
class RoomDeleteException(UpdateConflictException):
    id: int

    @property
    def message(self):
        return 'Failed to delete room'


@dataclass(eq=False)
class RoomIsUsedInLessonsException(InUseException):
    id: int

    @property
    def message(self):
        return 'Room is used in at least one lesson'


@dataclass(eq=False)
class OldAndNewRoomsAreSimilarException(ValidationException):
    old_number: str
    new_number: str

    @property
    def message(self):
        return 'Old and new room numbers are identical'


@dataclass(eq=False)
class OldAndNewRoomDescriptionsAreSimilarException(ValidationException):
    old_description: str
    new_description: str

    @property
    def message(self):
        return 'Old and new room descriptions are identical'
