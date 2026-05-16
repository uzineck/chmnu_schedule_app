from dataclasses import dataclass

from core.apps.common.cache.decorator import cache_decorator
from core.apps.schedule.exceptions.teacher import TeacherIsUsedInLessonsException
from core.apps.schedule.services.lesson import BaseLessonService
from core.apps.schedule.services.teacher import BaseTeacherService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class DeleteTeacherUseCase:
    teacher_service: BaseTeacherService
    lesson_service: BaseLessonService
    uuid_validator_service: BaseUuidValidatorService

    @cache_decorator.delete_caches([
        dict(model_prefix='teacher', func_prefix='all'),
        dict(model_prefix='teacher', func_prefix='list', filters='*', pagination_in='*'),
        dict(model_prefix='group', identifier='*', func_prefix='lessons', filters='*'),
        dict(model_prefix='teacher', identifier=lambda kw: kw['teacher_uuid'], func_prefix='lessons', filters='*'),
    ])
    def execute(self, teacher_uuid: str) -> None:
        self.uuid_validator_service.validate(uuid_str=teacher_uuid)

        teacher = self.teacher_service.get_by_uuid(teacher_uuid=teacher_uuid)
        if self.lesson_service.check_if_teacher_has_lessons(teacher_id=teacher.id):
            raise TeacherIsUsedInLessonsException(id=teacher.id)

        self.teacher_service.soft_delete(teacher_id=teacher.id)
