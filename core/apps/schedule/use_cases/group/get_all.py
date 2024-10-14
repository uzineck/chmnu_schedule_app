from dataclasses import dataclass
from typing import Iterable

from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.services.group import BaseGroupService


@dataclass
class GetAllGroupsUseCase:
    group_service: BaseGroupService

    def execute(self) -> Iterable[GroupEntity]:
        return self.group_service.get_all_groups()
