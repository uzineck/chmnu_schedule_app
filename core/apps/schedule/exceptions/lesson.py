from dataclasses import dataclass

from core.apps.common.exceptions import (
    NotFoundException,
    UpdateConflictException,
)


@dataclass(eq=False)
class LessonNotFoundException(NotFoundException):
    uuid: str | None = None
    id: int | None = None

    @property
    def message(self):
        return 'Lesson with given identifier was not found'


@dataclass(eq=False)
class LessonDeleteError(UpdateConflictException):
    uuid: str | None = None

    @property
    def message(self):
        return 'Failed to delete lesson'
