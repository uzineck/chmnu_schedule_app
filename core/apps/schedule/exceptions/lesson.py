from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class LessonNotFoundException(ServiceException):
    uuid: str | None = None
    id: str | None = None

    @property
    def message(self):
        return 'Пара з вказаним ідентифікатором не знайдено'


@dataclass(eq=False)
class LessonDeleteError(ServiceException):
    uuid: str | None = None

    @property
    def message(self):
        return 'Виникла помилка при видаленні пари'
