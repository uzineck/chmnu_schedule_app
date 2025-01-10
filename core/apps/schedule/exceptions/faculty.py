from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class FacultyNotFoundException(ServiceException):
    uuid: str | None = None
    id: int | None = None

    @property
    def message(self):
        return 'Факультет з вказаним ідентифікатором не знайдено'


@dataclass(eq=False)
class FacultyAlreadyExistsException(ServiceException):
    code_name: str | None = None
    name: str | None = None

    @property
    def message(self):
        return 'Факультет із зазначеними параметрами вже існує'


@dataclass(eq=False)
class FacultyUpdateException(ServiceException):
    id: int

    @property
    def message(self):
        return 'Виникла помилка при оновленні факультету'


@dataclass(eq=False)
class FacultyDeleteException(ServiceException):
    id: int

    @property
    def message(self):
        return 'Виникла помилка при видаленні факультету'


@dataclass(eq=False)
class OldAndNewFacultyNamesAreSimilarException(ServiceException):
    old_name: str
    new_name: str

    @property
    def message(self):
        return 'Стара і нова назва факультету збігаються'


@dataclass(eq=False)
class OldAndNewFacultyCodeNamesAreSimilarException(ServiceException):
    old_code_name: str
    new_code_name: str

    @property
    def message(self):
        return 'Стара і нова кодова назва факультету збігаються'
