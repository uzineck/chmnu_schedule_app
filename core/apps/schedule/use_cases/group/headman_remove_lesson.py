from dataclasses import dataclass

from core.apps.clients.services.client import BaseClientService
from core.apps.common.models import (
    ClientRole,
    Subgroup,
)
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.entities.group_lessons import GroupLesson as GroupLessonEntity
from core.apps.schedule.entities.lesson import Lesson as LessonEntity
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.services.group_lessons import BaseGroupLessonService
from core.apps.schedule.services.lesson import BaseLessonService
from core.apps.schedule.validators.group_lesson import BaseGroupLessonValidatorService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class HeadmanRemoveLessonFromGroupUseCase:
    client_service: BaseClientService
    group_service: BaseGroupService
    lesson_service: BaseLessonService
    group_lesson_service: BaseGroupLessonService

    uuid_validator_service: BaseUuidValidatorService
    group_lesson_validator_service: BaseGroupLessonValidatorService

    def execute(
            self,
            headman_email: str,
            subgroup: Subgroup | None,
            lesson_uuid: str,
    ) -> tuple[GroupEntity, LessonEntity]:
        self.uuid_validator_service.validate(uuid_str=lesson_uuid)

        client = self.client_service.get_by_email(client_email=headman_email)
        self.group_lesson_validator_service.validate(client_role=client.role, required_role=ClientRole.HEADMAN)

        group = self.group_service.get_group_from_headman(headman_id=client.id)
        self.group_lesson_validator_service.validate(group=group, subgroup=subgroup)

        lesson = self.lesson_service.get_by_uuid(lesson_uuid=lesson_uuid)

        group_lesson_entity = GroupLessonEntity(
            group=group,
            subgroup=subgroup,
            lesson=lesson,
        )

        self.group_lesson_service.delete(group_lesson=group_lesson_entity)

        if not self.group_lesson_service.check_lesson_belongs_to_any_group(lesson_id=lesson.id):
            self.lesson_service.delete_by_uuid(lesson_uuid=lesson_uuid)

        return group, lesson
