from dataclasses import dataclass

from core.apps.common.exceptions import AuthFailureException


@dataclass(eq=False)
class InvalidAuthDataException(AuthFailureException):
    code = "INVALID_CREDENTIALS"

    @property
    def message(self):
        return 'Invalid email or password'
