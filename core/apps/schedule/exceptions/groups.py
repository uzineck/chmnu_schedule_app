from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class GroupNotFoundException(ServiceException):
    group_number: str

    @property
    def message(self):
        return 'Group with provided number not found'


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
