import re
from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.clients.exceptions.client import ClientAlreadyExistsException
from core.apps.clients.services.client import BaseClientService
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

@dataclass
class EmailAlreadyInUseValidatorService(BaseEmailValidatorService):
    client_service: BaseClientService

    def validate(self, email: str, *args, **kwargs):
        if self.client_service.check_client_exists(client_email=email):
            raise ClientAlreadyExistsException(email=email)


class EmailPatternValidatorService(BaseEmailValidatorService):
    def validate(self, email: str, *args, **kwargs):
        pattern = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'
        if not re.match(pattern, email):
            raise InvalidEmailPatternException(email=email)


class SimilarOldAndNewEmailValidatorService(BaseEmailValidatorService):
    def validate(self, email: str, old_email: str | None = None, *args, **kwargs):
        if old_email is not None:
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
