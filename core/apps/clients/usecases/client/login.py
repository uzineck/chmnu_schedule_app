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
        client = self.client_service.get_by_email(client_email=email)
        self.client_service.validate_password(client_password=client.password, plain_password=password)

        tokens: TokenEntity = self.client_service.generate_tokens(client=client)
        raw_tokens = [self.client_service.get_raw_jwt(token) for token in [tokens.access_token, tokens.refresh_token]]
        self.issued_jwt_token_service.bulk_create(subject=client, raw_tokens=raw_tokens)

        return client, tokens
