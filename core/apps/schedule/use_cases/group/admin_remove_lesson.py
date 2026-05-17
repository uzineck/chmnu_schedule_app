from django.db import transaction

from dataclasses import dataclass

from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.models import Subgroup
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.entities.group_lessons import GroupLesson as GroupLessonEntity
from core.apps.schedule.entities.lesson import Lesson as LessonEntity
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.services.group_lessons import BaseGroupLessonService
from core.apps.schedule.services.lesson import BaseLessonService
from core.apps.schedule.validators.group_lesson import BaseGroupLessonValidatorService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class AdminRemoveLessonFromGroupUseCase:
    group_service: BaseGroupService
    lesson_service: BaseLessonService
    group_lesson_service: BaseGroupLessonService

    uuid_validator_service: BaseUuidValidatorService
    group_lesson_validator_service: BaseGroupLessonValidatorService

    @cache_decorator.delete_caches([
        dict(model_prefix='group', func_prefix='all'),
        dict(model_prefix='group', identifier=lambda kw: kw['group_uuid'], func_prefix='lessons', filters='*'),
        dict(
            model_prefix='teacher', identifier=lambda kw, res: res[1].teacher.uuid,
            func_prefix='lessons', filters='*',
        ),
    ])
    def execute(self, group_uuid: str, subgroup: Subgroup | None, lesson_uuid: str) -> tuple[GroupEntity, LessonEntity]:
        self.uuid_validator_service.validate(uuid_list=[group_uuid, lesson_uuid])

        group = self.group_service.get_by_uuid(group_uuid=group_uuid)
        self.group_lesson_validator_service.validate(group=group, subgroup=subgroup)

        lesson = self.lesson_service.get_by_uuid(lesson_uuid=lesson_uuid)

        group_lesson_entity = GroupLessonEntity(
            group=group,
            subgroup=subgroup,
            lesson=lesson,
        )

        with transaction.atomic():
            self.group_lesson_service.delete(group_lesson=group_lesson_entity)

            if not self.group_lesson_service.check_lesson_belongs_to_any_group(lesson_id=lesson.id):
                self.lesson_service.delete_by_uuid(lesson_uuid=lesson_uuid)

            self.group_service.bump_schedule_updated_at(group_id=group.id)

        return group, lesson
