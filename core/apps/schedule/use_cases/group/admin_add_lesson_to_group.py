from dataclasses import dataclass

from core.apps.common.models import Subgroup
from core.apps.schedule.entities.group_lessons import GroupLesson as GroupLessonEntity
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.services.group_lessons import BaseGroupLessonService
from core.apps.schedule.services.lesson import BaseLessonService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class AdminAddLessonToGroupUseCase:
    group_service: BaseGroupService
    lesson_service: BaseLessonService
    group_lesson_service: BaseGroupLessonService

    uuid_validator_service: BaseUuidValidatorService

    def execute(self, group_uuid: str, subgroup: Subgroup, lesson_uuid: str) -> None:
        self.uuid_validator_service.validate(uuid_list=[group_uuid, lesson_uuid])

        group = self.group_service.get_group_by_uuid(group_uuid=group_uuid)
        self.group_service.check_group_has_subgroups_subgroup(group=group, subgroup=subgroup)
        lesson = self.lesson_service.get_lessons_by_uuid(lesson_uuid=lesson_uuid)

        group_subgroup_lesson_entity = GroupLessonEntity(
            group=group,
            subgroup=subgroup,
            lesson=lesson,
        )

        existing_group_subgroup_lesson = self.group_lesson_service.check_group_subgroup_lesson_exists(
            group_lesson=group_subgroup_lesson_entity,
        )

        if not existing_group_subgroup_lesson:
            self.group_lesson_service.save_group_subgroup_lesson(group_lesson=group_subgroup_lesson_entity)
