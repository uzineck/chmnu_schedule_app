from dataclasses import dataclass

from core.apps.schedule.entities.faculty import Faculty as FacultyEntity
from core.apps.schedule.services.faculty import BaseFacultyService
from core.apps.schedule.validators.faculty import BaseFacultyValidatorService


@dataclass
class CreateFacultyUseCase:
    faculty_service: BaseFacultyService

    faculty_validator_service: BaseFacultyValidatorService

    def execute(self, name: str, code_name: str) -> FacultyEntity:
        self.faculty_validator_service.validate(name=name, code_name=code_name)

        faculty = self.faculty_service.create(name=name, code_name=code_name)

        return faculty
