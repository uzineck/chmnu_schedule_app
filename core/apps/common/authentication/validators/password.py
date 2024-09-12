import re
from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.common.authentication.exceptions import (
    InvalidPasswordPattern,
    PasswordsNotMatching,
)


class BasePasswordValidatorService(ABC):
    @abstractmethod
    def validate(self, password: str, verify_password: str | None = None):
        ...


class MatchingPasswordsValidatorService(BasePasswordValidatorService):
    def validate(self, password: str, verify_password: str | None = None):
        if not (password == verify_password):
            raise PasswordsNotMatching(password1=password, password2=verify_password)


class PasswordPatternValidatorService(BasePasswordValidatorService):
    def validate(self, password: str, *args, **kwargs):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!#%\^:;.,`~\'"*?&+=\-_]{8,}$'
        if not re.match(pattern, password):
            raise InvalidPasswordPattern(password=password)


@dataclass
class ComposedPasswordValidatorService(BasePasswordValidatorService):
    validators: list[BasePasswordValidatorService]

    def validate(self, password: str, verify_password: str | None = None):
        for validator in self.validators:
            validator.validate(password=password, verify_password=verify_password)
