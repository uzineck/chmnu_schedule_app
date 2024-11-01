from dataclasses import dataclass

from core.apps.common.models import TeachersDegree
from core.apps.schedule.entities.teacher import Teacher as TeacherEntity
from core.apps.schedule.services.teacher import BaseTeacherService
from core.apps.schedule.validators.teacher import BaseTeacherValidatorService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class UpdateTeacherRankUseCase:
    teacher_service: BaseTeacherService

    uuid_validator_service: BaseUuidValidatorService
    teacher_validator_service: BaseTeacherValidatorService

    def execute(self, teacher_uuid: str, rank: TeachersDegree) -> TeacherEntity:
        self.uuid_validator_service.validate(uuid_str=teacher_uuid)

        teacher = self.teacher_service.get_by_uuid(teacher_uuid=teacher_uuid)
        self.teacher_validator_service.validate(rank=rank, old_rank=teacher.rank)

        self.teacher_service.update_rank(teacher_id=teacher.id, rank=rank)
        updated_teacher = self.teacher_service.get_by_id(teacher_id=teacher.id)

        return updated_teacher
