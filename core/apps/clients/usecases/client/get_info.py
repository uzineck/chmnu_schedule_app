from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.services.client import BaseClientService
from core.apps.common.models import ClientRole
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.services.group import BaseGroupService


@dataclass
class GetClientInfoUseCase:
    client_service: BaseClientService

    def execute(self, email: str) -> ClientEntity:
        client = self.client_service.get_by_email(client_email=email)

        return client
