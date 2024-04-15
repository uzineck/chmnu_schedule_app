from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class SophomoreEmailException(ServiceException):
    email: str

    @property
    def message(self):
        return 'A sophomore with provided email not found'

