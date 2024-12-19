from dataclasses import dataclass

from core.apps.schedule.services.faculty import BaseFacultyService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class DeleteFacultyUseCase:
    faculty_service: BaseFacultyService

    uuid_validator_service: BaseUuidValidatorService

    def execute(self, faculty_uuid: str) -> None:
        self.uuid_validator_service.validate(uuid_str=faculty_uuid)

        faculty = self.faculty_service.get_by_uuid(faculty_uuid=faculty_uuid)
        self.faculty_service.delete(faculty_id=faculty.id)

        return None
