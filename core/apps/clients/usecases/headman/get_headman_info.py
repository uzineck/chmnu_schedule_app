from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.services.client import BaseClientService
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.services.groups import BaseGroupService


@dataclass
class GetHeadmanInfoUseCase:
    client_service: BaseClientService
    group_service: BaseGroupService

    def execute(self, email: str) -> tuple[GroupEntity, ClientEntity]:
        client = self.client_service.get_by_email(email=email)

        self.client_service.check_user_role(client.role, 'headman')

        group = self.group_service.get_group_from_headman(headman=client)
        return group, client






