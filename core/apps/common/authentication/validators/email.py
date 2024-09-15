import re
from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.common.authentication.validators.exceptions import (
    InvalidEmailPatternException,
    OldAndNewEmailsAreSimilarException,
)


class BaseEmailValidatorService(ABC):
    @abstractmethod
    def validate(
            self,
            email: str,
            old_email: str | None = None,
    ):
        ...


class EmailPatternValidatorService(BaseEmailValidatorService):
    def validate(self, email: str, *args, **kwargs):
        pattern = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'
        if not re.match(pattern, email):
            raise InvalidEmailPatternException(email=email)


class SimilarOldAndNewEmailValidatorService(BaseEmailValidatorService):
    def validate(self, email: str, old_email: str | None = None, *args, **kwargs):
        if email == old_email:
            raise OldAndNewEmailsAreSimilarException(old_email=old_email, new_email=email)


@dataclass
class ComposedEmailValidatorService(BaseEmailValidatorService):
    validators: list[BaseEmailValidatorService]

    def validate(
            self,
            email: str,
            old_email: str | None = None,
    ):
        for validator in self.validators:
            validator.validate(email=email, old_email=old_email)
