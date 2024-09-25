from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException
from core.apps.common.models import Subgroup


@dataclass(eq=False)
class GroupNumberNotFoundException(ServiceException):
    group_number: str

    @property
    def message(self):
        return 'Group with provided number not found'


@dataclass(eq=False)
class GroupUuidNotFoundException(ServiceException):
    uuid: str

    @property
    def message(self):
        return 'Group with provided uuid not found'


@dataclass(eq=False)
class GroupAlreadyExistsException(ServiceException):
    group_number: str

    @property
    def message(self):
        return 'Group with provided number already exists'


@dataclass(eq=False)
class HeadmanAssignedToAnotherGroupException(ServiceException):
    headman_email: str
    group_number: str

    @property
    def message(self):
        return 'Headman with provided email already assigned to another group'


@dataclass(eq=False)
class GroupWithoutSubgroupsInvalidSubgroupException(ServiceException):
    subgroup: Subgroup

    @property
    def message(self):
        return 'Group without subgroups cannot have subgroup B, only A'
