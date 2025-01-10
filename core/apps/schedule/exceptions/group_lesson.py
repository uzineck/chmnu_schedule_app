from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException
from core.apps.common.models import Subgroup


@dataclass(eq=False)
class GroupLessonDeleteError(ServiceException):
    group_number: str | None = None
    lesson_uuid: str | None = None
    subgroup: Subgroup | None = None

    @property
    def message(self):
        return 'Виникла помилка під час видалення пари групи'


@dataclass(eq=False)
class GroupLessonAlreadyExists(ServiceException):
    group_uuid: str | None = None
    lesson_uuid: str | None = None
    subgroup: Subgroup | None = None

    @property
    def message(self):
        return 'Група вже містить цю пару'
