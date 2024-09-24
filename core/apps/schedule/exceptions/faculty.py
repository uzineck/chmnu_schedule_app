from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class FacultyUuidNotFoundException(ServiceException):
    uuid: str

    @property
    def message(self):
        return 'Faculty with provided uuid not found'


@dataclass(eq=False)
class FacultyWithProvidedCodeNameAlreadyExists(ServiceException):
    code_name: str

    @property
    def message(self):
        return 'Faculty with provided code name already exists'
