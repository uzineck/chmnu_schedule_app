from dataclasses import dataclass
from transliterate import slugify

from core.apps.common.cache.decorator import cache_decorator
from core.apps.schedule.entities.subject import Subject as SubjectEntity
from core.apps.schedule.services.subject import BaseSubjectService
from core.apps.schedule.validators.subject import BaseSubjectValidatorService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class UpdateSubjectUseCase:
    subject_service: BaseSubjectService

    uuid_validator_service: BaseUuidValidatorService
    subject_validator_service: BaseSubjectValidatorService

    @cache_decorator.delete_caches([
        dict(model_prefix='subject', func_prefix='all'),
        dict(model_prefix='subject', func_prefix='list', filters='*', pagination_in='*'),
        dict(model_prefix='group', identifier='*', func_prefix='lessons', filters='*'),
        dict(model_prefix='teacher', identifier='*', func_prefix='lessons', filters='*'),
    ])
    def execute(self, subject_uuid: str, title: str) -> SubjectEntity:
        self.uuid_validator_service.validate(uuid_str=subject_uuid)

        subject = self.subject_service.get_by_uuid(subject_uuid=subject_uuid)
        self.subject_validator_service.validate(title=title, old_title=subject.title)

        slug = slugify(text=title, language_code='uk')
        self.subject_service.update(subject_id=subject.id, title=title, slug=slug)
        updated_subject = self.subject_service.get_by_id(subject_id=subject.id)

        return updated_subject
