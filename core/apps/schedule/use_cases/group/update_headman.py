from dataclasses import dataclass

from core.apps.clients.services.client import BaseClientService
from core.apps.common.models import ClientRole
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.services.groups import BaseGroupService


@dataclass
class UpdateGroupHeadmanUseCase:
    client_service: BaseClientService
    group_service: BaseGroupService

    def execute(self, group_number: str, headman_email: str) -> GroupEntity:
        group = self.group_service.get_group_by_number(group_number=group_number)
        headman = self.client_service.get_by_email(email=headman_email)
        self.client_service.check_user_role(headman.role, ClientRole.HEADMAN)
        return self.group_service.update_group_headman(group=group, headman=headman)



