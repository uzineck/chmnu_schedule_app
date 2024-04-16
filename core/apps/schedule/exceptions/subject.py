from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class SubjectNotFound(ServiceException):
    subject_info: str

    @property
    def message(self):
        return 'Subject with provided search query not found'


@dataclass(eq=False)
class SubjectAlreadyExistsException(ServiceException):
    title: str

    @property
    def message(self):
        return 'Subject with provided title already exists'



