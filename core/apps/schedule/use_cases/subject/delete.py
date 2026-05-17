from dataclasses import dataclass

from core.apps.common.cache.decorator import cache_decorator
from core.apps.schedule.exceptions.subject import SubjectIsUsedInLessonsException
from core.apps.schedule.services.lesson import BaseLessonService
from core.apps.schedule.services.subject import BaseSubjectService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class DeleteSubjectUseCase:
    subject_service: BaseSubjectService
    lesson_service: BaseLessonService

    uuid_validator_service: BaseUuidValidatorService

    @cache_decorator.delete_caches([
        dict(model_prefix='subject', func_prefix='all'),
        dict(model_prefix='subject', func_prefix='list', filters='*', pagination_in='*'),
    ])
    def execute(self, subject_uuid: str) -> None:
        self.uuid_validator_service.validate(uuid_str=subject_uuid)

        subject = self.subject_service.get_by_uuid(subject_uuid=subject_uuid)
        if self.lesson_service.check_if_subject_has_lessons(subject_id=subject.id):
            raise SubjectIsUsedInLessonsException(id=subject.id)

        self.subject_service.soft_delete(subject_id=subject.id)

        return None
