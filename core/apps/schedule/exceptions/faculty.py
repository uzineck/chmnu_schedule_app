from dataclasses import dataclass

from core.apps.common.exceptions import (
    AlreadyExistsException,
    InUseException,
    NotFoundException,
    UpdateConflictException,
    ValidationException,
)


@dataclass(eq=False)
class FacultyNotFoundException(NotFoundException):
    uuid: str | None = None
    id: int | None = None

    @property
    def message(self):
        return 'Faculty with given identifier was not found'


@dataclass(eq=False)
class FacultyAlreadyExistsException(AlreadyExistsException):
    code_name: str | None = None
    name: str | None = None

    @property
    def message(self):
        return 'Faculty with given parameters already exists'


@dataclass(eq=False)
class FacultyUpdateException(UpdateConflictException):
    id: int

    @property
    def message(self):
        return 'Failed to update faculty'


@dataclass(eq=False)
class FacultyDeleteException(UpdateConflictException):
    id: int

    @property
    def message(self):
        return 'Failed to delete faculty'


@dataclass(eq=False)
class FacultyHasGroupsException(InUseException):
    id: int

    @property
    def message(self):
        return 'Faculty has groups attached and cannot be deleted'


@dataclass(eq=False)
class OldAndNewFacultyNamesAreSimilarException(ValidationException):
    old_name: str
    new_name: str

    @property
    def message(self):
        return 'Old and new faculty names are identical'


@dataclass(eq=False)
class OldAndNewFacultyCodeNamesAreSimilarException(ValidationException):
    old_code_name: str
    new_code_name: str

    @property
    def message(self):
        return 'Old and new faculty code names are identical'
