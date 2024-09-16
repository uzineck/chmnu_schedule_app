from dataclasses import dataclass

from core.apps.clients.services.client import BaseClientService
from core.apps.common.models import Subgroup
from core.apps.schedule.entities.group_lessons import GroupLesson as GroupLessonEntity
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.services.group_lessons import BaseGroupLessonService
from core.apps.schedule.services.lesson import BaseLessonService


@dataclass
class HeadmanAddLessonToGroupUseCase:
    client_service: BaseClientService
    group_service: BaseGroupService
    lesson_service: BaseLessonService

    group_lesson_service: BaseGroupLessonService

    def execute(self, headman_email: str, subgroup: Subgroup, lesson_uuid: str) -> GroupLessonEntity:
        headman = self.client_service.get_by_email(headman_email)
        group = self.group_service.get_group_from_headman(headman=headman)
        lesson = self.lesson_service.get_lessons_by_uuid(lesson_uuid=lesson_uuid)
        group_lesson_entity = GroupLessonEntity(
            group=group,
            subgroup=subgroup,
            lesson=lesson,
        )
        existing_group_subgroup_lesson = self.group_lesson_service.check_group_subgroup_lesson_exists(
            group_lesson=group_lesson_entity,
        )

        if not existing_group_subgroup_lesson:
            saved_lesson = self.group_lesson_service.save_group_subgroup_lesson(group_lesson=group_lesson_entity)
            return saved_lesson
        else:
            return existing_group_subgroup_lesson
