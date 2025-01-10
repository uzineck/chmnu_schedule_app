from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class SubjectNotFoundException(ServiceException):
    uuid: str | None = None
    id: int | None = None

    @property
    def message(self):
        return 'Дисципліни із зазначеним ідентифікатором не знайдено'


@dataclass(eq=False)
class SubjectAlreadyExistException(ServiceException):
    title: str

    @property
    def message(self):
        return 'Дисципліна із зазначеними параметрами вже існує'


@dataclass(eq=False)
class SubjectUpdateException(ServiceException):
    id: int

    @property
    def message(self):
        return 'Виникла помилка при оновленні дисципліни'


@dataclass(eq=False)
class SubjectDeleteException(ServiceException):
    id: int

    @property
    def message(self):
        return 'Виникла помилка при видаленні дисципліни'


@dataclass(eq=False)
class OldAndNewSubjectsAreSimilarException(ServiceException):
    old_title: str
    new_title: str

    @property
    def message(self):
        return 'Стара і нова назва дисципліни збігаються'
