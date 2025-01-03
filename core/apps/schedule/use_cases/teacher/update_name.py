from dataclasses import dataclass

from core.apps.schedule.entities.teacher import Teacher as TeacherEntity
from core.apps.schedule.services.teacher import BaseTeacherService
from core.apps.schedule.validators.teacher import BaseTeacherValidatorService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class UpdateTeacherNameUseCase:
    teacher_service: BaseTeacherService

    uuid_validator_service: BaseUuidValidatorService
    teacher_validator_service: BaseTeacherValidatorService

    def execute(self, teacher_uuid: str, first_name: str, last_name: str, middle_name: str) -> TeacherEntity:
        self.uuid_validator_service.validate(uuid_str=teacher_uuid)

        teacher = self.teacher_service.get_by_uuid(teacher_uuid=teacher_uuid)
        self.teacher_validator_service.validate(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            old_first_name=teacher.first_name,
            old_last_name=teacher.last_name,
            old_middle_name=teacher.middle_name,
        )

        self.teacher_service.update_name(
            teacher_id=teacher.id,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
        )
        updated_teacher = self.teacher_service.get_by_id(teacher_id=teacher.id)

        return updated_teacher
