from dataclasses import dataclass

from core.apps.schedule.entities.faculty import Faculty as FacultyEntity
from core.apps.schedule.services.faculty import BaseFacultyService


@dataclass
class CreateFacultyUseCase:
    faculty_service: BaseFacultyService

    def execute(self, name: str, code_name: str) -> FacultyEntity:
        faculty = self.faculty_service.create(name=name, code_name=code_name)

        return faculty

