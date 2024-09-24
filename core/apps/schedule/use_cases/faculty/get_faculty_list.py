from collections.abc import Iterable
from dataclasses import dataclass

from core.api.filters import PaginationIn
from core.apps.common.filters import SearchFilter
from core.apps.schedule.entities.faculty import Faculty as FacultyEntity
from core.apps.schedule.services.faculty import BaseFacultyService


@dataclass
class GetFacultyListUseCase:
    faculty_service: BaseFacultyService

    def execute(self, filters: SearchFilter, pagination: PaginationIn) -> tuple[Iterable[FacultyEntity], int]:
        faculty_list = self.faculty_service.get_faculty_list(filters=filters, pagination=pagination)
        faculty_count = self.faculty_service.get_faculty_count(filters=filters)

        return faculty_list, faculty_count

