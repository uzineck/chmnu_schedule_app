from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class InvalidAuthDataException(ServiceException):
    password: str | None = None

    @property
    def message(self):
        return 'Incorrect email or password'
