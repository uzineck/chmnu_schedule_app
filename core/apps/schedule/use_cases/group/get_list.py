from collections.abc import Iterable
from dataclasses import dataclass

from core.api.filters import PaginationIn
from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.cache.timeouts import Timeout
from core.apps.common.filters import SearchFilter
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.services.group import BaseGroupService


@dataclass
class GetGroupListUseCase:
    group_service: BaseGroupService

    @cache_decorator.get_or_set_cache(model_prefix='group', func_prefix='list', timeout=Timeout.WEEK)
    def execute(
            self,
            filters: SearchFilter,
            pagination_in: PaginationIn,
    ) -> tuple[Iterable[GroupEntity], int]:
        group_list = self.group_service.get_list(filters=filters, pagination=pagination_in)
        group_count = self.group_service.get_count(filters=filters)

        return group_list, group_count
