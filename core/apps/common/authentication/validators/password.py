import re
from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.common.authentication.validators.exceptions import (
    InvalidPasswordPatternException,
    OldAndNewPasswordsAreSimilarException,
    PasswordsNotMatchingException,
)


class BasePasswordValidatorService(ABC):
    @abstractmethod
    def validate(
            self,
            password: str,
            verify_password: str | None = None,
            old_password: str | None = None,
    ):
        ...


class MatchingVerifyPasswordsValidatorService(BasePasswordValidatorService):
    def validate(
            self,
            password: str,
            verify_password: str | None = None,
            *args,
            **kwargs,
    ):
        if verify_password is None:
            raise ValueError("verify_password is required")
        if password != verify_password:
            raise PasswordsNotMatchingException()


class PasswordPatternValidatorService(BasePasswordValidatorService):
    def validate(self, password: str, *args, **kwargs):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!#%\^:;.,`~\'"*?&+=\-_()]{8,}$'
        if not re.match(pattern, password):
            raise InvalidPasswordPatternException()


class SimilarOldAndNewPasswordValidatorService(BasePasswordValidatorService):
    def validate(self, password: str, old_password: str | None = None, *args, **kwargs):
        if old_password is not None:
            if old_password == password:
                raise OldAndNewPasswordsAreSimilarException()


@dataclass
class ComposedPasswordValidatorService(BasePasswordValidatorService):
    validators: list[BasePasswordValidatorService]

    def validate(
            self,
            password: str,
            verify_password: str | None = None,
            old_password: str | None = None,
    ):
        for validator in self.validators:
            validator.validate(password=password, verify_password=verify_password, old_password=old_password)
