import uuid
from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.schedule.exceptions.uuid_validator import InvalidUuidFormatStringException


class BaseUuidValidatorService(ABC):
    @abstractmethod
    def validate(
            self,
            uuid_str: str | None = None,
            uuid_list: list[str] | None = None,
    ):
        ...


@dataclass
class InvalidUuidTypeValidatorService(BaseUuidValidatorService):

    def validate(self, uuid_str: str | None = None, uuid_list: list[str] | None = None, *args, **kwargs):
        if uuid_str:
            self._validate_single_uuid(uuid_str=uuid_str)

        if uuid_list:
            for uuid_str_from_list in uuid_list:
                self._validate_single_uuid(uuid_str=uuid_str_from_list)

    def _validate_single_uuid(self, uuid_str: str):
        try:
            check_uuid = uuid.UUID(uuid_str)
            if uuid_str != str(check_uuid):
                raise InvalidUuidFormatStringException(uuid_str=uuid_str)
        except ValueError:
            raise InvalidUuidFormatStringException(uuid_str=uuid_str)


@dataclass
class ComposedUuidValidatorService(BaseUuidValidatorService):
    validators: list[BaseUuidValidatorService]

    def validate(
            self,
            uuid_str: str | None = None,
            uuid_list: list[str] | None = None,
    ):
        for validator in self.validators:
            validator.validate(uuid_str=uuid_str, uuid_list=uuid_list)
