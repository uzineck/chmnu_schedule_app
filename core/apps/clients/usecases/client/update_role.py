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
        self.issued_jwt_token_service.create(
            subject=updated_client,
            jti=self.client_service.get_jti_from_token(token=tokens.refresh_token),
            device_id=self.client_service.get_device_id_from_token(token=tokens.refresh_token),
            expiration_time=self.client_service.get_expiration_time_from_token(token=tokens.refresh_token),
        )

        return updated_client, tokens
