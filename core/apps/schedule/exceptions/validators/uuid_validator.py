from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class InvalidUuidFormatStringException(ServiceException):
    uuid_str: str

    @property
    def message(self):
        return 'Неправильний формат рядка UUID'
