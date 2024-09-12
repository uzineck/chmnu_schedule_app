import re
from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.common.authentication.exceptions import InvalidEmailPattern


class BaseEmailValidatorService(ABC):
    @abstractmethod
    def validate(self, email: str):
        ...


class EmailPatternValidatorService(BaseEmailValidatorService):
    def validate(self, email: str):
        pattern = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'
        if not re.match(pattern, email):
            raise InvalidEmailPattern(email=email)


@dataclass
class ComposedEmailValidatorService(BaseEmailValidatorService):
    validators: list[BaseEmailValidatorService]

    def validate(self, email: str):
        for validator in self.validators:
            validator.validate(email=email)
