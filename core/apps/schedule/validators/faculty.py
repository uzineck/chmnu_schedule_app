from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.schedule.exceptions.faculty import (
    FacultyAlreadyExistsException,
    OldAndNewFacultyCodeNamesAreSimilarException,
    OldAndNewFacultyNamesAreSimilarException,
)
from core.apps.schedule.services.faculty import BaseFacultyService


class BaseFacultyValidatorService(ABC):

    @abstractmethod
    def validate(
            self,
            name: str | None = None,
            code_name: str | None = None,
            old_name: str | None = None,
            old_code_name: str | None = None,
    ):
        ...


@dataclass
class FacultyAlreadyExistsByNameValidatorService(BaseFacultyValidatorService):
    faculty_service: BaseFacultyService

    def validate(self, name: str | None = None, *args, **kwargs):
        if name:
            if self.faculty_service.check_exists_by_name(faculty_name=name):
                raise FacultyAlreadyExistsException(name=name)


@dataclass
class FacultyAlreadyExistsByCodeNameValidatorService(BaseFacultyValidatorService):
    faculty_service: BaseFacultyService

    def validate(self, code_name: str | None = None, *args, **kwargs):
        if code_name:
            if self.faculty_service.check_exists_by_code_name(faculty_code_name=code_name):
                raise FacultyAlreadyExistsException(code_name=code_name)


class SimilarOldAndNewFacultyNameValidatorService(BaseFacultyValidatorService):
    def validate(self, name: str | None = None, old_name: str | None = None, *args, **kwargs):
        if name and old_name:
            if name == old_name:
                raise OldAndNewFacultyNamesAreSimilarException(old_name=old_name, new_name=name)


class SimilarOldAndNewFacultyCodeNameValidatorService(BaseFacultyValidatorService):
    def validate(self, code_name: str | None = None, old_code_name: str | None = None, *args, **kwargs):
        if code_name and old_code_name:
            if code_name == old_code_name:
                raise OldAndNewFacultyCodeNamesAreSimilarException(old_code_name=old_code_name, new_code_name=code_name)


@dataclass
class ComposedFacultyValidatorService(BaseFacultyValidatorService):
    validators: list[BaseFacultyValidatorService]

    def validate(
            self,
            name: str | None = None,
            code_name: str | None = None,
            old_name: str | None = None,
            old_code_name: str | None = None,
    ):
        for validator in self.validators:
            validator.validate(
                name=name,
                code_name=code_name,
                old_name=old_name,
                old_code_name=old_code_name,
            )
