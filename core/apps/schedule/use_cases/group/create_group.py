from dataclasses import dataclass

from core.apps.clients.services.client import BaseClientService
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.services.groups import BaseGroupService


@dataclass
class CreateGroupUseCase:
    client_service: BaseClientService
    group_service: BaseGroupService

    def execute(self, group_number: str, headman_email: str, has_subgroups: bool) -> GroupEntity:
        headman = self.client_service.get_by_email(email=headman_email)

        return self.group_service.get_or_create(
            group_number=group_number,
            has_subgroups=has_subgroups,
            headman_id=headman.id,
        )




