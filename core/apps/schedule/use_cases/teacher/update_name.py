from dataclasses import dataclass

from core.apps.common.cache.decorator import cache_decorator
from core.apps.schedule.entities.teacher import Teacher as TeacherEntity
from core.apps.schedule.services.teacher import BaseTeacherService
from core.apps.schedule.validators.teacher import BaseTeacherValidatorService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class UpdateTeacherNameUseCase:
    teacher_service: BaseTeacherService

    uuid_validator_service: BaseUuidValidatorService
    teacher_validator_service: BaseTeacherValidatorService

    @cache_decorator.delete_caches([
        dict(model_prefix='teacher', func_prefix='all'),
        dict(model_prefix='teacher', func_prefix='list', filters='*', pagination_in='*'),
        dict(model_prefix='teacher', identifier=lambda kw: kw['teacher_uuid'], func_prefix='*', filters='*'),
        dict(model_prefix='group', identifier='*', func_prefix='lessons', filters='*'),
    ])
    def execute(self, teacher_uuid: str, first_name: str, last_name: str, middle_name: str) -> TeacherEntity:
        self.uuid_validator_service.validate(uuid_str=teacher_uuid)

        teacher = self.teacher_service.get_by_uuid(teacher_uuid=teacher_uuid)
        self.teacher_validator_service.validate(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            old_first_name=teacher.first_name,
            old_last_name=teacher.last_name,
            old_middle_name=teacher.middle_name,
        )

        self.teacher_service.update_name(
            teacher_id=teacher.id,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
        )
        updated_teacher = self.teacher_service.get_by_id(teacher_id=teacher.id)

        return updated_teacher
