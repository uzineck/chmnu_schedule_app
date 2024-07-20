from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.services.client import BaseClientService


@dataclass
class UpdateClientRoleUseCase:
    client_service: BaseClientService

    def execute(self, client_email: str, new_role: str) -> tuple[ClientEntity, str]:
        client = self.client_service.get_by_email(email=client_email)
        updated_client = self.client_service.update_role(client=client, new_role=new_role)

        return updated_client, self.client_service.generate_token(client=updated_client)
