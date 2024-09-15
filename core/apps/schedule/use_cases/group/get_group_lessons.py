from dataclasses import dataclass
from typing import Iterable

from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.entities.lesson import Lesson as LessonEntity
from core.apps.schedule.filters.group import GroupFilter
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.services.lesson import BaseLessonService


@dataclass
class GetGroupLessonsUseCase:
    group_service: BaseGroupService
    lesson_service: BaseLessonService

    def execute(self, group_number: str, filters: GroupFilter) -> tuple[GroupEntity, Iterable[LessonEntity]]:
        group = self.group_service.get_group_by_number(group_number=group_number)
        group_qs = self.group_service.get_qs_for_group(filters=filters)
        lessons = self.lesson_service.get_lessons_for_group(group_number=group_number, group_query=group_qs)
        return group, lessons




