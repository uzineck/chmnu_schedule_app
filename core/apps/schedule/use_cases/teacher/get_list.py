from collections.abc import Iterable
from dataclasses import dataclass

from core.api.filters import PaginationIn
from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.cache.timeouts import Timeout
from core.apps.schedule.entities.teacher import Teacher as TeacherEntity
from core.apps.schedule.filters.teacher import TeacherFilter
from core.apps.schedule.services.teacher import BaseTeacherService


@dataclass
class GetTeacherListUseCase:
    teacher_service: BaseTeacherService

    @cache_decorator.get_or_set_cache(model_prefix='teacher', func_prefix='list', timeout=Timeout.WEEK)
    def execute(self, filters: TeacherFilter, pagination_in: PaginationIn) -> tuple[Iterable[TeacherEntity], int]:
        teacher_list = self.teacher_service.get_list(filters=filters, pagination=pagination_in)
        teacher_count = self.teacher_service.get_count(filters=filters)

        return teacher_list, teacher_count
