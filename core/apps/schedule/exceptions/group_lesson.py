from dataclasses import dataclass

from core.apps.common.exceptions import (
    AlreadyExistsException,
    UpdateConflictException,
)
from core.apps.common.models import Subgroup


@dataclass(eq=False)
class GroupLessonDeleteError(UpdateConflictException):
    group_number: str | None = None
    lesson_uuid: str | None = None
    subgroup: Subgroup | None = None

    @property
    def message(self):
        return 'Failed to delete group lesson'


@dataclass(eq=False)
class GroupLessonAlreadyExists(AlreadyExistsException):
    group_uuid: str | None = None
    lesson_uuid: str | None = None
    subgroup: Subgroup | None = None

    @property
    def message(self):
        return 'Group already contains this lesson'
