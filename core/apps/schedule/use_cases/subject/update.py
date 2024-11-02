from dataclasses import dataclass
from transliterate import slugify

from core.apps.schedule.entities.subject import Subject as SubjectEntity
from core.apps.schedule.services.subject import BaseSubjectService
from core.apps.schedule.validators.subject import BaseSubjectValidatorService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class UpdateSubjectUseCase:
    subject_service: BaseSubjectService

    uuid_validator_service: BaseUuidValidatorService
    subject_validator_service: BaseSubjectValidatorService

    def execute(self, subject_uuid: str, title: str) -> SubjectEntity:
        self.uuid_validator_service.validate(uuid_str=subject_uuid)

        subject = self.subject_service.get_by_uuid(subject_uuid=subject_uuid)
        self.subject_validator_service.validate(title=title, old_title=subject.title)

        slug = slugify(text=title, language_code='uk')
        self.subject_service.update(subject_id=subject.id, title=title, slug=slug)
        updated_subject = self.subject_service.get_by_id(subject_id=subject.id)

        return updated_subject
