from dataclasses import dataclass

from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.models import TeachersDegree
from core.apps.schedule.entities.teacher import Teacher as TeacherEntity
from core.apps.schedule.services.teacher import BaseTeacherService
from core.apps.schedule.validators.teacher import BaseTeacherValidatorService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class UpdateTeacherRankUseCase:
    teacher_service: BaseTeacherService

    uuid_validator_service: BaseUuidValidatorService
    teacher_validator_service: BaseTeacherValidatorService

    @cache_decorator.delete_caches([
        dict(model_prefix='teacher', func_prefix='all'),
        dict(model_prefix='teacher', func_prefix='list', filters='*', pagination_in='*'),
        dict(model_prefix='teacher', identifier=lambda kw: kw['teacher_uuid'], func_prefix='*', filters='*'),
        dict(model_prefix='group', identifier='*', func_prefix='lessons', filters='*'),
    ])
    def execute(self, teacher_uuid: str, rank: TeachersDegree) -> TeacherEntity:
        self.uuid_validator_service.validate(uuid_str=teacher_uuid)

        teacher = self.teacher_service.get_by_uuid(teacher_uuid=teacher_uuid)
        self.teacher_validator_service.validate(rank=rank, old_rank=teacher.rank)

        self.teacher_service.update_rank(teacher_id=teacher.id, rank=rank)
        updated_teacher = self.teacher_service.get_by_id(teacher_id=teacher.id)

        return updated_teacher
