from dataclasses import dataclass

from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.cache.timeouts import Timeout
from core.apps.schedule.entities.faculty import Faculty as FacultyEntity
from core.apps.schedule.services.faculty import BaseFacultyService


@dataclass
class GetAllFacultiesUseCase:
    faculty_service: BaseFacultyService

    @cache_decorator.get_or_set_cache(model_prefix='faculty', func_prefix='all', timeout=Timeout.WEEK)
    def execute(self) -> list[FacultyEntity]:
        return list(self.faculty_service.get_all())
