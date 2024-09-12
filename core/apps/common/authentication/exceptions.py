from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class PasswordsNotMatching(ServiceException):
    password1: str
    password2: str

    @property
    def message(self):
        return 'Provided passwords do not match'


@dataclass(eq=False)
class InvalidPasswordPattern(ServiceException):
    password: str

    @property
    def message(self):
        return (
            'The provided password does not meet the required security criteria: it must be at least 8 characters '
            'long, contain both uppercase and lowercase letters, at least one digit, and cat contain only this '
            'symbols !@#$%^:;.,&*?`~\'"+=-_'
        )


@dataclass(eq=False)
class InvalidEmailPattern(ServiceException):
    email: str

    @property
    def message(self):
        return 'The provided email does not meet the required email pattern: example@gmail.com (only @gmail.com)'

