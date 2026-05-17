from collections.abc import Iterable
from dataclasses import dataclass

from core.api.filters import PaginationIn
from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.cache.timeouts import Timeout
from core.apps.common.filters import SearchFilter
from core.apps.schedule.entities.faculty import Faculty as FacultyEntity
from core.apps.schedule.services.faculty import BaseFacultyService


@dataclass
class GetFacultyListUseCase:
    faculty_service: BaseFacultyService

    @cache_decorator.get_or_set_cache(model_prefix='faculty', func_prefix='list', timeout=Timeout.WEEK)
    def execute(
            self,
            filters: SearchFilter,
            pagination_in: PaginationIn,
    ) -> tuple[Iterable[FacultyEntity], int]:
        faculty_list = self.faculty_service.get_list(filters=filters, pagination=pagination_in)
        faculty_count = self.faculty_service.get_count(filters=filters)

        return faculty_list, faculty_count
