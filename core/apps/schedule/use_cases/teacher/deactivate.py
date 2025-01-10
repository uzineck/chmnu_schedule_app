from dataclasses import dataclass

from core.apps.schedule.exceptions.teacher import TeacherIsUsedInLessonsException
from core.apps.schedule.services.lesson import BaseLessonService
from core.apps.schedule.services.teacher import BaseTeacherService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class DeactivateTeacherUseCase:
    teacher_service: BaseTeacherService
    lesson_service: BaseLessonService
    uuid_validator_service: BaseUuidValidatorService

    def execute(self, teacher_uuid: str) -> None:
        self.uuid_validator_service.validate(uuid_str=teacher_uuid)

        teacher = self.teacher_service.get_by_uuid(teacher_uuid=teacher_uuid)
        if self.lesson_service.check_if_teacher_has_lessons(teacher_id=teacher.id):
            raise TeacherIsUsedInLessonsException(id=teacher.id)

        self.teacher_service.update_is_active(
            teacher_id=teacher.id,
            is_active=False,
        )

        return None
