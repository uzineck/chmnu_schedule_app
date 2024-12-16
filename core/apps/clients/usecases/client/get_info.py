from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.services.client import BaseClientService


@dataclass
class GetClientInfoUseCase:
    client_service: BaseClientService

    def execute(self, email: str) -> ClientEntity:
        client = self.client_service.get_by_email(client_email=email)

        return client
