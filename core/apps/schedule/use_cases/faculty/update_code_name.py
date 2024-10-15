from dataclasses import dataclass

from core.apps.schedule.entities.faculty import Faculty as FacultyEntity
from core.apps.schedule.services.faculty import BaseFacultyService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class UpdateFacultyCodeNameUseCase:
    faculty_service: BaseFacultyService

    uuid_validator_service: BaseUuidValidatorService

    def execute(self, faculty_uuid: str, code_name: str) -> FacultyEntity:
        self.uuid_validator_service.validate(uuid_str=faculty_uuid)

        faculty = self.faculty_service.get_by_uuid(faculty_uuid=faculty_uuid)
        self.faculty_service.update_code_name(faculty_id=faculty.id, new_code_name=code_name)
        updated_faculty = self.faculty_service.get_by_id(faculty_id=faculty.id)

        return updated_faculty
