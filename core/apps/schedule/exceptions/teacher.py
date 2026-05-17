from dataclasses import dataclass

from core.apps.common.exceptions import (
    AlreadyExistsException,
    InUseException,
    NotFoundException,
    UpdateConflictException,
    ValidationException,
)


@dataclass(eq=False)
class TeacherNotFoundException(NotFoundException):
    uuid: str | None = None
    id: int | None = None

    @property
    def message(self):
        return 'Teacher with given identifier was not found'


@dataclass(eq=False)
class TeacherAlreadyExistsException(AlreadyExistsException):
    first_name: str
    last_name: str
    middle_name: str

    @property
    def message(self):
        return 'Teacher with given parameters already exists'


@dataclass(eq=False)
class TeacherUpdateException(UpdateConflictException):
    id: int

    @property
    def message(self):
        return 'Failed to update teacher'


@dataclass(eq=False)
class TeacherDeleteException(UpdateConflictException):
    id: int

    @property
    def message(self):
        return 'Failed to delete teacher'


@dataclass(eq=False)
class TeacherIsUsedInLessonsException(InUseException):
    id: int

    @property
    def message(self):
        return 'Teacher is used in at least one lesson'


@dataclass(eq=False)
class OldAndNewTeacherNamesAreSimilarException(ValidationException):
    first_name: str
    last_name: str
    middle_name: str
    old_first_name: str
    old_last_name: str
    old_middle_name: str

    @property
    def message(self):
        return 'Old and new teacher names are identical'


@dataclass(eq=False)
class OldAndNewTeacherRanksAreSimilarException(ValidationException):
    old_rank: str
    new_rank: str

    @property
    def message(self):
        return 'Old and new teacher ranks are identical'
