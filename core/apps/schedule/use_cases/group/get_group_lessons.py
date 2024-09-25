from dataclasses import dataclass
from typing import Iterable

from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.entities.lesson import Lesson as LessonEntity
from core.apps.schedule.filters.group import GroupLessonFilter
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.services.group_lessons import BaseGroupLessonService
from core.apps.schedule.services.lesson import BaseLessonService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class GetGroupLessonsUseCase:
    group_service: BaseGroupService
    lesson_service: BaseLessonService
    group_lesson_service: BaseGroupLessonService

    uuid_validator_service: BaseUuidValidatorService

    def execute(self, group_uuid: str, filters: GroupLessonFilter) -> tuple[GroupEntity, Iterable[LessonEntity]]:
        self.uuid_validator_service.validate(uuid_str=group_uuid)

        group = self.group_service.get_group_by_uuid(group_uuid=group_uuid)
        self.group_service.check_group_has_subgroups_subgroup(group=group, subgroup=filters.subgroup)
        lessons = self.lesson_service.get_lessons_for_group(group_id=group.id, filter_query=filters)
        return group, lessons
