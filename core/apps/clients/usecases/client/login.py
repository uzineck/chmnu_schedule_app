from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.entities.token import Token as TokenEntity
from core.apps.clients.services.client import BaseClientService
from core.apps.clients.services.issuedjwttoken import BaseIssuedJwtTokenService


@dataclass
class LoginClientUseCase:
    client_service: BaseClientService
    issued_jwt_token_service: BaseIssuedJwtTokenService

    def execute(self, email: str, password: str) -> tuple[ClientEntity, TokenEntity]:
        client = self.client_service.validate_client(email=email, password=password)

        tokens: TokenEntity = self.client_service.generate_tokens(client=client)
        self.issued_jwt_token_service.create(
            subject=client,
            jti=self.client_service.get_jti_from_token(token=tokens.refresh_token),
            device_id=self.client_service.get_device_id_from_token(token=tokens.refresh_token),
            expiration_time=self.client_service.get_expiration_time_from_token(token=tokens.refresh_token),
        )

        return client, tokens
