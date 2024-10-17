from dataclasses import dataclass

from core.apps.common.models import Subgroup
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.entities.group_lessons import GroupLesson as GroupLessonEntity
from core.apps.schedule.entities.lesson import Lesson as LessonEntity
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.services.group_lessons import BaseGroupLessonService
from core.apps.schedule.services.lesson import BaseLessonService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class AdminRemoveLessonFromGroupUseCase:
    group_service: BaseGroupService
    lesson_service: BaseLessonService
    group_lesson_service: BaseGroupLessonService

    uuid_validator_service: BaseUuidValidatorService

    def execute(self, group_uuid: str, subgroup: Subgroup, lesson_uuid: str) -> tuple[GroupEntity, LessonEntity]:
        self.uuid_validator_service.validate(uuid_list=[group_uuid, lesson_uuid])

        group = self.group_service.get_by_uuid(group_uuid=group_uuid)
        self.group_service.check_if_group_has_subgroup(group=group, subgroup=subgroup)
        lesson = self.lesson_service.get_by_uuid(lesson_uuid=lesson_uuid)
        group_lesson_entity = GroupLessonEntity(
            group=group,
            subgroup=subgroup,
            lesson=lesson,
        )

        self.group_lesson_service.delete(group_lesson=group_lesson_entity)

        return group, lesson
