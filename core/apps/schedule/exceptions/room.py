from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class RoomNotFoundException(ServiceException):
    uuid: str | None = None
    id: int | None = None
    number: str | None = None

    @property
    def message(self):
        return 'Аудиторії з вказаним ідентифікатором не знайдено'


@dataclass(eq=False)
class RoomAlreadyExistException(ServiceException):
    number: str

    @property
    def message(self):
        return 'Аудиторія з вказаним номером вже існує'


@dataclass(eq=False)
class RoomUpdateException(ServiceException):
    id: int

    @property
    def message(self):
        return 'Виникла помилка при оновленні аудиторії'


@dataclass(eq=False)
class RoomDeleteException(ServiceException):
    id: int

    @property
    def message(self):
        return 'Виникла помилка при видаленні аудиторії'


@dataclass(eq=False)
class OldAndNewRoomsAreSimilarException(ServiceException):
    old_number: str
    new_number: str

    @property
    def message(self):
        return 'Старий і новий номер аудиторії збігаються'


@dataclass(eq=False)
class OldAndNewRoomDescriptionsAreSimilarException(ServiceException):
    old_description: str
    new_description: str

    @property
    def message(self):
        return 'Старий і новий опис аудиторії збігаються'
