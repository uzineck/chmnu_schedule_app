from dataclasses import dataclass

from core.apps.common.exceptions import (
    AlreadyExistsException,
    InUseException,
    NotFoundException,
    UpdateConflictException,
    ValidationException,
)


@dataclass(eq=False)
class SubjectNotFoundException(NotFoundException):
    uuid: str | None = None
    id: int | None = None

    @property
    def message(self):
        return 'Subject with given identifier was not found'


@dataclass(eq=False)
class SubjectAlreadyExistException(AlreadyExistsException):
    title: str

    @property
    def message(self):
        return 'Subject with given parameters already exists'


@dataclass(eq=False)
class SubjectUpdateException(UpdateConflictException):
    id: int

    @property
    def message(self):
        return 'Failed to update subject'


@dataclass(eq=False)
class SubjectDeleteException(UpdateConflictException):
    id: int

    @property
    def message(self):
        return 'Failed to delete subject'


@dataclass(eq=False)
class SubjectIsUsedInLessonsException(InUseException):
    id: int

    @property
    def message(self):
        return 'Subject is used in at least one lesson'


@dataclass(eq=False)
class OldAndNewSubjectsAreSimilarException(ValidationException):
    old_title: str
    new_title: str

    @property
    def message(self):
        return 'Old and new subject titles are identical'
