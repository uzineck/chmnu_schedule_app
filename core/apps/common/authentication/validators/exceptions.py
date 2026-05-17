from dataclasses import dataclass

from core.apps.common.exceptions import ValidationException


@dataclass(eq=False)
class PasswordsNotMatchingException(ValidationException):
    @property
    def message(self):
        return 'Provided passwords do not match'


@dataclass(eq=False)
class InvalidPasswordPatternException(ValidationException):
    @property
    def message(self):
        return (
            'The provided password does not meet the required security criteria: it must be at least 8 characters '
            'long, contain both uppercase and lowercase letters, at least one digit, and can contain only this '
            'symbols !@#$%^:;.,&*?`~\'"+=-_'
        )


@dataclass(eq=False)
class OldAndNewPasswordsAreSimilarException(ValidationException):
    @property
    def message(self):
        return 'Old and new passwords are identical'


@dataclass(eq=False)
class OldAndNewEmailsAreSimilarException(ValidationException):
    old_email: str
    new_email: str

    @property
    def message(self):
        return 'Old and new emails are identical'
