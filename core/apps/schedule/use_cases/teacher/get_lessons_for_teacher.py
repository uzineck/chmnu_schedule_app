from dataclasses import dataclass
from typing import Iterable

from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.entities.lesson import Lesson as LessonEntity
from core.apps.schedule.entities.teacher import Teacher as TeacherEntity
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.services.lesson import BaseLessonService
from core.apps.schedule.services.teacher import BaseTeacherService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class GetLessonsForTeacherUseCase:
    teacher_service: BaseTeacherService
    group_service: BaseGroupService
    lesson_service: BaseLessonService

    uuid_validator_service: BaseUuidValidatorService

    def execute(self, teacher_uuid: str) -> tuple[TeacherEntity, Iterable[LessonEntity], dict[int, [GroupEntity]]]:
        self.uuid_validator_service.validate(uuid_str=teacher_uuid)

        teacher = self.teacher_service.get_teacher_by_uuid(teacher_uuid=teacher_uuid)
        lessons = self.lesson_service.get_lessons_for_teacher(teacher_id=teacher.id)
        groups = {}
        for lesson in lessons:
            groups[lesson.id] = self.group_service.get_groups_from_lesson(lesson_id=lesson.id)
        return teacher, lessons, groups
