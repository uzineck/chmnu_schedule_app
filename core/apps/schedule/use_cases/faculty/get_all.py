from collections.abc import Iterable
from dataclasses import dataclass

from core.apps.schedule.entities.faculty import Faculty as FacultyEntity
from core.apps.schedule.services.faculty import BaseFacultyService


@dataclass
class GetAllFacultiesUseCase:
    faculty_service: BaseFacultyService

    def execute(self) -> Iterable[FacultyEntity]:
        faculties = self.faculty_service.get_all()

        return faculties
