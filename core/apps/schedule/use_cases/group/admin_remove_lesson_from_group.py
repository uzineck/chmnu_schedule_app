from dataclasses import dataclass

from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.services.lesson import BaseLessonService


@dataclass
class AdminRemoveLessonFromGroupUseCase:
    group_service: BaseGroupService
    lesson_service: BaseLessonService

    def execute(self, group_number: str, lesson_id: int) -> GroupEntity:
        lesson = self.lesson_service.get_lessons_by_id(lesson_id=lesson_id)
        updated_group = self.group_service.remove_lesson(group_number=group_number, lesson_id=lesson.id)
        return updated_group




