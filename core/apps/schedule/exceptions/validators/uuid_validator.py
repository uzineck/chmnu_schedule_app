from dataclasses import dataclass

from core.apps.common.exceptions import ValidationException


@dataclass(eq=False)
class InvalidUuidFormatStringException(ValidationException):
    uuid_str: str

    @property
    def message(self):
        return 'Invalid UUID string format'
