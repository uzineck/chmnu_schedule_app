from dataclasses import dataclass

from core.apps.common.models import TeachersDegree
from core.apps.schedule.entities.teacher import Teacher as TeacherEntity
from core.apps.schedule.services.teacher import BaseTeacherService
from core.apps.schedule.validators.teacher import BaseTeacherValidatorService


@dataclass
class CreateTeacherUseCase:
    teacher_service: BaseTeacherService

    teacher_validator_service: BaseTeacherValidatorService

    def execute(self, first_name: str, last_name: str, middle_name: str, rank: TeachersDegree) -> TeacherEntity:
        self.teacher_validator_service.validate(first_name=first_name, last_name=last_name, middle_name=middle_name)

        teacher = self.teacher_service.create(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            rank=rank,
        )

        return teacher
