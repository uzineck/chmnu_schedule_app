from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class GroupNotFoundException(ServiceException):
    group_number: str

    @property
    def message(self):
        return 'Group with provided number not found'
