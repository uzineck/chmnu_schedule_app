from dataclasses import dataclass

from core.apps.schedule.services.teacher import BaseTeacherService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class DeactivateTeacherUseCase:
    teacher_service: BaseTeacherService

    uuid_validator_service: BaseUuidValidatorService

    def execute(self, teacher_uuid: str) -> None:
        self.uuid_validator_service.validate(uuid_str=teacher_uuid)

        teacher = self.teacher_service.get_by_uuid(teacher_uuid=teacher_uuid)
        self.teacher_service.update_teacher_is_active(
            teacher_id=teacher.id,
            is_active=False,
        )

        return None
