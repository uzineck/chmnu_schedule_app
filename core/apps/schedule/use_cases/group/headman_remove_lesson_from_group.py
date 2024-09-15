from dataclasses import dataclass

from core.apps.clients.services.client import BaseClientService
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.services.lesson import BaseLessonService


@dataclass
class HeadmanRemoveLessonFromGroupUseCase:
    client_service: BaseClientService
    group_service: BaseGroupService
    lesson_service: BaseLessonService

    def execute(self, headman_email: str, lesson_id: int) -> GroupEntity:
        headman = self.client_service.get_by_email(headman_email)
        group = self.group_service.get_group_from_headman(headman=headman)
        lesson = self.lesson_service.get_lessons_by_id(lesson_id=lesson_id)
        updated_group = self.group_service.remove_lesson(group_number=group.number, lesson_id=lesson.id)
        return updated_group




