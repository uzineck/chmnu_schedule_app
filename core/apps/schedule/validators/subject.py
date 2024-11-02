from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.schedule.exceptions.subject import (
    OldAndNewSubjectsAreSimilarException,
    SubjectAlreadyExistException,
)
from core.apps.schedule.services.subject import BaseSubjectService


class BaseSubjectValidatorService(ABC):

    @abstractmethod
    def validate(
            self,
            title: str | None = None,
            old_title: str | None = None,
    ):
        ...


@dataclass
class SubjectAlreadyExistsValidatorService(BaseSubjectValidatorService):
    subject_service: BaseSubjectService

    def validate(self, title: str | None = None, *args, **kwargs):
        if title:
            if self.subject_service.check_exists_by_title(title=title):
                raise SubjectAlreadyExistException(title=title)


class SimilarOldAndNewSubjectTitlesValidatorService(BaseSubjectValidatorService):
    def validate(self, title: str | None = None, old_title: str | None = None, *args, **kwargs):
        if title and old_title:
            if title == old_title:
                raise OldAndNewSubjectsAreSimilarException(old_title=old_title, new_title=old_title)


@dataclass
class ComposedSubjectValidatorService(BaseSubjectValidatorService):
    validators: list[BaseSubjectValidatorService]

    def validate(
            self,
            title: str | None = None,
            old_title: str | None = None,
    ):
        for validator in self.validators:
            validator.validate(title=title, old_title=old_title)
