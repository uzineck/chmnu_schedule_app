from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException
from core.apps.common.models import Subgroup


@dataclass(eq=False)
class GroupNotFoundException(ServiceException):
    number: str | None = None
    uuid: str | None = None
    id: int | None = None

    @property
    def message(self):
        return 'Group with provided identifier not found'


@dataclass(eq=False)
class GroupAlreadyExistsException(ServiceException):
    group_number: str | None = None
    headman_id: int | None = None

    @property
    def message(self):
        return 'Group with provided parameters already exists'


@dataclass(eq=False)
class HeadmanAssignedToAnotherGroupException(ServiceException):
    headman_email: str

    @property
    def message(self):
        return 'Headman with provided email already assigned to another group'


@dataclass(eq=False)
class GroupWithoutSubgroupsInvalidSubgroupException(ServiceException):
    subgroup: Subgroup

    @property
    def message(self):
        return 'Group without subgroups cannot have subgroup'


@dataclass(eq=False)
class GroupWithSubgroupsInvalidSubgroupException(ServiceException):

    @property
    def message(self):
        return 'Group with subgroups cannot but have a subgroup'


@dataclass(eq=False)
class HeadmanNotAssignedToAnyGroup(ServiceException):
    headman_id: int

    @property
    def message(self):
        return 'Headman is not assigned to any group'


@dataclass(eq=False)
class GroupHeadmanUpdateException(ServiceException):
    group_id: int | None = None
    headman_id: int | None = None

    @property
    def message(self):
        return 'An error occurred while updating groups` headman'
