from dataclasses import dataclass

from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.services.groups import BaseGroupService


@dataclass
class GetGroupInfoUseCase:
    group_service: BaseGroupService

    def execute(self, group_number: str) -> GroupEntity:
        return self.group_service.get_group_by_number(group_number=group_number)