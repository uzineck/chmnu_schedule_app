from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.services.client import BaseClientService
from core.apps.common.models import ClientRole
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.services.group import BaseGroupService


@dataclass
class GetHeadmanInfoUseCase:
    client_service: BaseClientService
    group_service: BaseGroupService

    def execute(self, email: str) -> tuple[GroupEntity, ClientEntity] | tuple[None, ClientEntity]:
        client = self.client_service.get_by_email(email=email)

        self.client_service.check_client_role(client.role, ClientRole.HEADMAN)

        group = self.group_service.get_group_from_headman(headman=client)
        return group, client
