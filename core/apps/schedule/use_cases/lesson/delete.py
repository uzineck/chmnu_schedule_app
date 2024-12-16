from dataclasses import dataclass

from core.apps.schedule.services.group_lessons import BaseGroupLessonService
from core.apps.schedule.services.lesson import BaseLessonService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class DeleteLessonUseCase:
    lesson_service: BaseLessonService
    group_lesson_service: BaseGroupLessonService

    uuid_validator_service: BaseUuidValidatorService

    def execute(self, lesson_uuid: str) -> None:
        self.uuid_validator_service.validate(uuid_str=lesson_uuid)

        lesson = self.lesson_service.get_by_uuid(lesson_uuid=lesson_uuid)

        if not self.group_lesson_service.check_lesson_belongs_to_any_group(lesson_id=lesson.id):
            self.lesson_service.delete_by_uuid(lesson_uuid=lesson_uuid)
