from collections.abc import Iterable
from dataclasses import dataclass

from core.api.filters import PaginationIn
from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.cache.timeouts import Timeout
from core.apps.common.filters import SearchFilter
from core.apps.schedule.entities.subject import Subject as SubjectEntity
from core.apps.schedule.services.subject import BaseSubjectService


@dataclass
class GetSubjectListUseCase:
    subject_service: BaseSubjectService

    @cache_decorator.get_or_set_cache(model_prefix='subject', func_prefix='list', timeout=Timeout.WEEK)
    def execute(self, filters: SearchFilter, pagination_in: PaginationIn) -> tuple[Iterable[SubjectEntity], int]:
        subject_list = self.subject_service.get_list(filters=filters, pagination=pagination_in)
        subject_count = self.subject_service.get_count(filters=filters)

        return subject_list, subject_count
