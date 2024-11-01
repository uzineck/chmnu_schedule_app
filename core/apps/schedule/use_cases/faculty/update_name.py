from dataclasses import dataclass

from core.apps.schedule.entities.faculty import Faculty as FacultyEntity
from core.apps.schedule.services.faculty import BaseFacultyService
from core.apps.schedule.validators.faculty import BaseFacultyValidatorService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class UpdateFacultyNameUseCase:
    faculty_service: BaseFacultyService

    uuid_validator_service: BaseUuidValidatorService
    faculty_validator_service: BaseFacultyValidatorService

    def execute(self, faculty_uuid: str, name: str) -> FacultyEntity:
        self.uuid_validator_service.validate(uuid_str=faculty_uuid)

        faculty = self.faculty_service.get_by_uuid(faculty_uuid=faculty_uuid)
        self.faculty_validator_service.validate(name=name, old_name=faculty.name)

        self.faculty_service.update_name(faculty_id=faculty.id, new_name=name)
        updated_faculty = self.faculty_service.get_by_id(faculty_id=faculty.id)

        return updated_faculty
