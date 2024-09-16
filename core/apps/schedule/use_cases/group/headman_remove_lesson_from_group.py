from dataclasses import dataclass

from core.apps.clients.services.client import BaseClientService
from core.apps.common.models import Subgroup
from core.apps.schedule.entities.group_lessons import GroupLesson as GroupLessonEntity
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.services.group_lessons import BaseGroupLessonService
from core.apps.schedule.services.lesson import BaseLessonService


@dataclass
class HeadmanRemoveLessonFromGroupUseCase:
    client_service: BaseClientService
    group_service: BaseGroupService
    lesson_service: BaseLessonService

    group_lesson_service: BaseGroupLessonService

    def execute(self, headman_email: str, subgroup: Subgroup, lesson_uuid: str) -> None:
        headman = self.client_service.get_by_email(headman_email)
        group = self.group_service.get_group_from_headman(headman=headman)
        lesson = self.lesson_service.get_lessons_by_uuid(lesson_uuid=lesson_uuid)
        group_lesson_entity = GroupLessonEntity(
            group=group,
            subgroup=subgroup,
            lesson=lesson,
        )

        self.group_lesson_service.delete_group_subgroup_lesson(group_lesson=group_lesson_entity)




