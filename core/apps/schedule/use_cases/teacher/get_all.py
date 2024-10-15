from dataclasses import dataclass
from typing import Iterable

from core.apps.schedule.entities.teacher import Teacher as TeacherEntity
from core.apps.schedule.services.teacher import BaseTeacherService


@dataclass
class GetAllTeachersUseCase:
    teacher_service: BaseTeacherService

    def execute(self) -> Iterable[TeacherEntity]:
        return self.teacher_service.get_all()
