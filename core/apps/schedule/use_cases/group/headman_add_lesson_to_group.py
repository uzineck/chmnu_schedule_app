from dataclasses import dataclass

from core.apps.clients.services.client import BaseClientService
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.services.groups import BaseGroupService
from core.apps.schedule.services.lessons import BaseLessonService


@dataclass
class HeadmanAddLessonToGroupUseCase:
    client_service: BaseClientService
    group_service: BaseGroupService
    lesson_service: BaseLessonService

    def execute(self, headman_email: str, lesson_id: int) -> GroupEntity:
        headman = self.client_service.get_by_email(headman_email)
        group = self.group_service.get_group_from_headman(headman=headman)
        lesson = self.lesson_service.get_lessons_by_id(lesson_id=lesson_id)
        updated_group = self.group_service.add_lesson(group_number=group.number, lesson_id=lesson.id)
        return updated_group




