from dataclasses import dataclass

from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.cache.timeouts import Timeout
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.services.group import BaseGroupService


@dataclass
class GetAllGroupsUseCase:
    group_service: BaseGroupService

    @cache_decorator.get_or_set_cache(model_prefix='group', func_prefix='all', timeout=Timeout.WEEK)
    def execute(self) -> list[GroupEntity]:
        return list(self.group_service.get_all())
