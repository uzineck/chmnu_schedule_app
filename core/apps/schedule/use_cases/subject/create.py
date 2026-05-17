from dataclasses import dataclass
from transliterate import slugify

from core.apps.common.cache.decorator import cache_decorator
from core.apps.schedule.entities.subject import Subject as SubjectEntity
from core.apps.schedule.services.subject import BaseSubjectService
from core.apps.schedule.validators.subject import BaseSubjectValidatorService


@dataclass
class CreateSubjectUseCase:
    subject_service: BaseSubjectService

    subject_validator_service: BaseSubjectValidatorService

    @cache_decorator.delete_caches([
        dict(model_prefix='subject', func_prefix='all'),
        dict(model_prefix='subject', func_prefix='list', filters='*', pagination_in='*'),
    ])
    def execute(self, title: str) -> SubjectEntity:
        self.subject_validator_service.validate(title=title)

        existing = self.subject_service.find_any_by_title(title=title)
        if existing is not None and not existing.is_active:
            self.subject_service.restore(subject_id=existing.id)
            return self.subject_service.get_by_id(subject_id=existing.id)

        slug = slugify(text=title, language_code='uk')
        return self.subject_service.create(title=title, slug=slug)
