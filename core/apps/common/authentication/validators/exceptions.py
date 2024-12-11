from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class PasswordsNotMatchingException(ServiceException):
    password1: str
    password2: str

    @property
    def message(self):
        return 'Provided passwords do not match'


@dataclass(eq=False)
class InvalidPasswordPatternException(ServiceException):
    password: str

    @property
    def message(self):
        return (
            'The provided password does not meet the required security criteria: it must be at least 8 characters '
            'long, contain both uppercase and lowercase letters, at least one digit, and can contain only this '
            'symbols !@#$%^:;.,&*?`~\'"+=-_'
        )


@dataclass(eq=False)
class OldAndNewPasswordsAreSimilarException(ServiceException):
    old_password: str
    new_password: str

    @property
    def message(self):
        return 'Old password and the new one are similar'


@dataclass(eq=False)
class InvalidEmailPatternException(ServiceException):
    email: str

    @property
    def message(self):
        return 'The provided email does not meet the required email pattern: example@gmail.com (only @gmail.com)'


@dataclass(eq=False)
class OldAndNewEmailsAreSimilarException(ServiceException):
    old_email: str
    new_email: str

    @property
    def message(self):
        return 'Old email and the new one are similar'
