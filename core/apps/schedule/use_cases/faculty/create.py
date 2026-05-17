from dataclasses import dataclass

from core.apps.common.cache.decorator import cache_decorator
from core.apps.schedule.entities.faculty import Faculty as FacultyEntity
from core.apps.schedule.services.faculty import BaseFacultyService
from core.apps.schedule.validators.faculty import BaseFacultyValidatorService


@dataclass
class CreateFacultyUseCase:
    faculty_service: BaseFacultyService

    faculty_validator_service: BaseFacultyValidatorService

    @cache_decorator.delete_caches([
        dict(model_prefix='faculty', func_prefix='all'),
        dict(model_prefix='faculty', func_prefix='list', filters='*', pagination_in='*'),
    ])
    def execute(self, name: str, code_name: str) -> FacultyEntity:
        self.faculty_validator_service.validate(name=name, code_name=code_name)

        existing = self.faculty_service.find_any_by_code_name(faculty_code_name=code_name)
        if existing is not None and not existing.is_active:
            self.faculty_service.restore(faculty_id=existing.id)
            return self.faculty_service.get_by_id(faculty_id=existing.id)

        return self.faculty_service.create(name=name, code_name=code_name)
