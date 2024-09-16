from dataclasses import dataclass

from core.apps.common.models import Subgroup
from core.apps.schedule.entities.group_lessons import GroupLesson as GroupLessonEntity
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

    def execute(self, group_uuid: str, subgroup: Subgroup, lesson_uuid: str) -> None:
        self.uuid_validator_service.validate(uuid_list=[group_uuid, lesson_uuid])

        group = self.group_service.get_group_by_uuid(group_uuid=group_uuid)
        lesson = self.lesson_service.get_lessons_by_uuid(lesson_uuid=lesson_uuid)
        group_lesson_entity = GroupLessonEntity(
            group=group,
            subgroup=subgroup,
            lesson=lesson,
        )

        self.group_lesson_service.delete_group_subgroup_lesson(group_lesson=group_lesson_entity)








