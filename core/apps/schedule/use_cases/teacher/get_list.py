from collections.abc import Iterable
from dataclasses import dataclass

from core.api.filters import PaginationIn
from core.apps.schedule.entities.teacher import Teacher as TeacherEntity
from core.apps.schedule.filters.teacher import TeacherFilter
from core.apps.schedule.services.teacher import BaseTeacherService


@dataclass
class GetTeacherListUseCase:
    teacher_service: BaseTeacherService

    def execute(self, filters: TeacherFilter, pagination: PaginationIn) -> tuple[Iterable[TeacherEntity], int]:
        teacher_list = self.teacher_service.get_list(filters=filters, pagination=pagination)
        teacher_count = self.teacher_service.get_count(filters=filters)

        return teacher_list, teacher_count
