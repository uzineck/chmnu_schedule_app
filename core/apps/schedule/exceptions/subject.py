from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class SubjectNotFoundException(ServiceException):
    subject_info: str

    @property
    def message(self):
        return 'Subject with provided search query not found'


@dataclass(eq=False)
class SubjectIdNotFoundException(ServiceException):
    subject_id: int

    @property
    def message(self):
        return f'Subject with provided id not found ID({self.subject_id})'


@dataclass(eq=False)
class SubjectAlreadyExistException(ServiceException):
    title: str

    @property
    def message(self):
        return 'Subject with provided title already exists'



