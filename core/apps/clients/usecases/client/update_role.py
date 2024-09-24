from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.entities.token import Token as TokenEntity
from core.apps.clients.services.client import BaseClientService
from core.apps.clients.services.issuedjwttoken import BaseIssuedJwtTokenService
from core.apps.common.models import ClientRole


@dataclass
class UpdateClientRoleUseCase:
    client_service: BaseClientService
    issued_jwt_token_service: BaseIssuedJwtTokenService

    def execute(self, client_email: str, new_role: ClientRole) -> tuple[ClientEntity, TokenEntity]:
        client = self.client_service.get_by_email(email=client_email)
        updated_client = self.client_service.update_role(client=client, new_role=new_role)

        tokens: TokenEntity = self.client_service.generate_tokens(client=updated_client)
        raw_tokens = [self.client_service.get_raw_jwt(token) for token in [tokens.access_token, tokens.refresh_token]]
        self.issued_jwt_token_service.bulk_create(subject=updated_client, raw_tokens=raw_tokens)

        return updated_client, tokens
