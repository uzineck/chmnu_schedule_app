from dataclasses import dataclass

from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.cache.timeouts import Timeout
from core.apps.schedule.entities.subject import Subject as SubjectEntity
from core.apps.schedule.services.subject import BaseSubjectService


@dataclass
class GetAllSubjectsUseCase:
    subject_service: BaseSubjectService

    @cache_decorator.get_or_set_cache(model_prefix='subject', func_prefix='all', timeout=Timeout.WEEK)
    def execute(self) -> list[SubjectEntity]:
        return list(self.subject_service.get_all())
