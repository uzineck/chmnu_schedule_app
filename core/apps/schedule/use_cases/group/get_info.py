from dataclasses import dataclass

from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.cache.timeouts import Timeout
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class GetGroupInfoUseCase:
    group_service: BaseGroupService

    uuid_validator_service: BaseUuidValidatorService

    @cache_decorator.get_or_set_cache(
        model_prefix='group',
        identifier=lambda kw: kw['group_uuid'],
        func_prefix='info',
        timeout=Timeout.DAY,
    )
    def execute(self, group_uuid: str) -> GroupEntity:
        self.uuid_validator_service.validate(uuid_str=group_uuid)

        return self.group_service.get_by_uuid(group_uuid=group_uuid)
