from dataclasses import dataclass

from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.models import TeachersDegree
from core.apps.schedule.entities.teacher import Teacher as TeacherEntity
from core.apps.schedule.services.teacher import BaseTeacherService
from core.apps.schedule.validators.teacher import BaseTeacherValidatorService


@dataclass
class CreateTeacherUseCase:
    teacher_service: BaseTeacherService

    teacher_validator_service: BaseTeacherValidatorService

    @cache_decorator.delete_caches([
        dict(model_prefix='teacher', func_prefix='all'),
        dict(model_prefix='teacher', func_prefix='list', filters='*', pagination_in='*'),
    ])
    def execute(self, first_name: str, last_name: str, middle_name: str, rank: TeachersDegree) -> TeacherEntity:
        self.teacher_validator_service.validate(first_name=first_name, last_name=last_name, middle_name=middle_name)

        existing = self.teacher_service.find_any_by_full_name(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
        )
        if existing is not None and not existing.is_active:
            self.teacher_service.restore(teacher_id=existing.id)
            self.teacher_service.update_rank(teacher_id=existing.id, rank=rank)
            return self.teacher_service.get_by_id(teacher_id=existing.id)

        return self.teacher_service.create(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            rank=rank,
        )
