from dataclasses import dataclass

from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.cache.timeouts import Timeout
from core.apps.schedule.entities.teacher import Teacher as TeacherEntity
from core.apps.schedule.entities.views import LessonWithGroupsView
from core.apps.schedule.filters.group import LessonFilter
from core.apps.schedule.services.lesson import BaseLessonService
from core.apps.schedule.services.teacher import BaseTeacherService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class GetLessonsForTeacherUseCase:
    teacher_service: BaseTeacherService
    lesson_service: BaseLessonService

    uuid_validator_service: BaseUuidValidatorService

    @cache_decorator.get_or_set_cache(
        model_prefix='teacher',
        identifier=lambda kw: kw['teacher_uuid'],
        func_prefix='lessons',
        timeout=Timeout.HALF_DAY,
    )
    def execute(
            self,
            teacher_uuid: str,
            filters: LessonFilter,
    ) -> tuple[TeacherEntity, list[LessonWithGroupsView]]:
        self.uuid_validator_service.validate(uuid_str=teacher_uuid)

        teacher = self.teacher_service.get_by_uuid(teacher_uuid=teacher_uuid)
        views = self.lesson_service.get_lessons_with_groups_for_teacher(
            teacher_id=teacher.id,
            filter_query=filters,
        )

        return teacher, views
