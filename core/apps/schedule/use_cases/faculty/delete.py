from dataclasses import dataclass

from core.apps.common.cache.decorator import cache_decorator
from core.apps.schedule.exceptions.faculty import FacultyHasGroupsException
from core.apps.schedule.services.faculty import BaseFacultyService
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class DeleteFacultyUseCase:
    faculty_service: BaseFacultyService
    group_service: BaseGroupService

    uuid_validator_service: BaseUuidValidatorService

    @cache_decorator.delete_caches([
        dict(model_prefix='faculty', func_prefix='all'),
        dict(model_prefix='faculty', func_prefix='list', filters='*', pagination_in='*'),
    ])
    def execute(self, faculty_uuid: str) -> None:
        self.uuid_validator_service.validate(uuid_str=faculty_uuid)

        faculty = self.faculty_service.get_by_uuid(faculty_uuid=faculty_uuid)
        if self.group_service.check_faculty_has_groups(faculty_id=faculty.id):
            raise FacultyHasGroupsException(id=faculty.id)

        self.faculty_service.soft_delete(faculty_id=faculty.id)

        return None
