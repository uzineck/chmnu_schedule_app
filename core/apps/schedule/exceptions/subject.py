from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class SubjectNotFoundException(ServiceException):
    subject_info: str

    @property
    def message(self):
        return 'Subject with provided search query not found'


@dataclass(eq=False)
class SubjectUuidNotFoundException(ServiceException):
    uuid: str

    @property
    def message(self):
        return f'Subject with provided id not found ID({self.uuid})'


@dataclass(eq=False)
class SubjectAlreadyExistException(ServiceException):
    uuid: str
    title: str

    @property
    def message(self):
        return 'Subject with provided uuid(title) already exists'



