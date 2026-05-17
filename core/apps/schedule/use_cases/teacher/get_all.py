from dataclasses import dataclass

from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.cache.timeouts import Timeout
from core.apps.schedule.entities.teacher import Teacher as TeacherEntity
from core.apps.schedule.services.teacher import BaseTeacherService


@dataclass
class GetAllTeachersUseCase:
    teacher_service: BaseTeacherService

    @cache_decorator.get_or_set_cache(model_prefix='teacher', func_prefix='all', timeout=Timeout.WEEK)
    def execute(self) -> list[TeacherEntity]:
        return list(self.teacher_service.get_all())
