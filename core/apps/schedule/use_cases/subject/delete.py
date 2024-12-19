from dataclasses import dataclass

from core.apps.schedule.services.subject import BaseSubjectService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class DeleteSubjectUseCase:
    subject_service: BaseSubjectService

    uuid_validator_service: BaseUuidValidatorService

    def execute(self, subject_uuid: str) -> None:
        self.uuid_validator_service.validate(uuid_str=subject_uuid)

        subject = self.subject_service.get_by_uuid(subject_uuid=subject_uuid)
        self.subject_service.delete(subject_id=subject.id)

        return None
