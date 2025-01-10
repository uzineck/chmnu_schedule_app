from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class TeacherNotFoundException(ServiceException):
    uuid: str | None = None
    id: int | None = None

    @property
    def message(self):
        return 'Викладача з вказаним ідентифікатором не знайдено'


@dataclass(eq=False)
class TeacherAlreadyExistsException(ServiceException):
    first_name: str
    last_name: str
    middle_name: str

    @property
    def message(self):
        return 'Викладач із зазначеними параметрами вже існує'


@dataclass(eq=False)
class TeacherUpdateException(ServiceException):
    id: int

    @property
    def message(self):
        return 'Виникла помилка під час оновлення викладача'


@dataclass(eq=False)
class TeacherIsUsedInLessonsException(ServiceException):
    id: int

    @property
    def message(self):
        return 'Викладач використовується у деякому занятті'


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
        return 'Старе і нове ім\'я викладача збігаються'


@dataclass(eq=False)
class OldAndNewTeacherRanksAreSimilarException(ServiceException):
    old_rank: str
    new_rank: str

    @property
    def message(self):
        return 'Старе і нове звання викладача збігаються'
