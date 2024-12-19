from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.services.client import BaseClientService
from core.apps.clients.services.issuedjwttoken import BaseIssuedJwtTokenService
from core.apps.common.models import ClientRole


@dataclass
class UpdateClientRoleUseCase:
    client_service: BaseClientService
    issued_jwt_token_service: BaseIssuedJwtTokenService

    def execute(self, email: str, new_role: ClientRole) -> ClientEntity:
        client = self.client_service.get_by_email(client_email=email)
        self.client_service.update_role(client_id=client.id, new_role=new_role)
        updated_client = self.client_service.get_by_id(client_id=client.id)

        self.issued_jwt_token_service.revoke_client_tokens(subject=updated_client)

        return updated_client
