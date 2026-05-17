from dataclasses import dataclass

from core.apps.common.exceptions import (
    AlreadyExistsException,
    InUseException,
    NotFoundException,
    UpdateConflictException,
    ValidationException,
)
from core.apps.common.models import Subgroup


@dataclass(eq=False)
class GroupNotFoundException(NotFoundException):
    number: str | None = None
    uuid: str | None = None
    id: int | None = None

    @property
    def message(self):
        return 'Group with given identifier was not found'


@dataclass(eq=False)
class GroupAlreadyExistsException(AlreadyExistsException):
    group_number: str | None = None
    headman_id: int | None = None

    @property
    def message(self):
        return 'Group with given parameters already exists'


@dataclass(eq=False)
class HeadmanAssignedToAnotherGroupException(AlreadyExistsException):
    headman_email: str

    @property
    def message(self):
        return 'Headman with given email is already assigned to another group'


@dataclass(eq=False)
class GroupWithoutSubgroupsInvalidSubgroupException(ValidationException):
    subgroup: Subgroup

    @property
    def message(self):
        return 'Group without subgroups cannot have a subgroup'


@dataclass(eq=False)
class GroupWithSubgroupsInvalidSubgroupException(ValidationException):

    @property
    def message(self):
        return 'Group with subgroups must have a subgroup specified'


@dataclass(eq=False)
class HeadmanNotAssignedToAnyGroup(NotFoundException):
    headman_id: int

    @property
    def message(self):
        return 'Headman is not assigned to any group'


@dataclass(eq=False)
class GroupHeadmanUpdateException(UpdateConflictException):
    group_id: int | None = None
    headman_id: int | None = None

    @property
    def message(self):
        return 'Failed to update group headman'


@dataclass(eq=False)
class GroupHasActiveScheduleException(InUseException):
    uuid: str | None = None
    id: int | None = None

    @property
    def message(self):
        return 'Group still has an active schedule and cannot be deleted'
