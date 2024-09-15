from dataclasses import dataclass

from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.services.group import BaseGroupService


@dataclass
class GetGroupInfoUseCase:
    group_service: BaseGroupService

    def execute(self, group_uuid: str) -> GroupEntity:
        return self.group_service.get_group_by_uuid(group_uuid=group_uuid)
