from dataclasses import dataclass
from transliterate import slugify

from core.apps.schedule.entities.subject import Subject as SubjectEntity
from core.apps.schedule.services.subject import BaseSubjectService
from core.apps.schedule.validators.subject import BaseSubjectValidatorService


@dataclass
class CreateSubjectUseCase:
    subject_service: BaseSubjectService

    subject_validator_service: BaseSubjectValidatorService

    def execute(self, title: str) -> SubjectEntity:
        self.subject_validator_service.validate(title=title)

        slug = slugify(text=title, language_code='uk')
        subject = self.subject_service.create(title=title, slug=slug)

        return subject
