from dataclasses import dataclass

from core.apps.common.cache.decorator import cache_decorator
from core.apps.schedule.exceptions.group import GroupHasActiveScheduleException
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.services.group_lessons import BaseGroupLessonService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class DeleteGroupUseCase:
    group_service: BaseGroupService
    group_lesson_service: BaseGroupLessonService

    uuid_validator_service: BaseUuidValidatorService

    @cache_decorator.delete_caches([
        dict(model_prefix='group', func_prefix='all'),
        dict(model_prefix='group', func_prefix='list', filters='*', pagination_in='*'),
        dict(model_prefix='group', identifier=lambda kw: kw['group_uuid'], func_prefix='*', filters='*'),
    ])
    def execute(self, group_uuid: str) -> None:
        self.uuid_validator_service.validate(uuid_str=group_uuid)

        group = self.group_service.get_by_uuid(group_uuid=group_uuid)
        if self.group_lesson_service.check_group_has_any_lesson(group_id=group.id):
            raise GroupHasActiveScheduleException(uuid=group_uuid, id=group.id)

        self.group_service.soft_delete(group_id=group.id)

        return None
