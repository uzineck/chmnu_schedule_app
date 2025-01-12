from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.services.client import BaseClientService
from core.apps.clients.services.issuedjwttoken import BaseIssuedJwtTokenService
from core.apps.clients.services.role import BaseRoleService
from core.apps.common.models import ClientRole


@dataclass
class UpdateClientRoleUseCase:
    client_service: BaseClientService
    role_service: BaseRoleService
    issued_jwt_token_service: BaseIssuedJwtTokenService

    def execute(self, email: str, roles: list[ClientRole]) -> ClientEntity:
        client = self.client_service.get_by_email(client_email=email)
        fetched_roles = self.role_service.fetch_roles(roles=roles)

        self.client_service.update_roles(client_id=client.id, roles=fetched_roles)
        updated_client = self.client_service.get_by_id(client_id=client.id)

        self.issued_jwt_token_service.revoke_client_tokens(subject=updated_client)

        return updated_client
