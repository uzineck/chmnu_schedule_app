from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.entities.token import Token as TokenEntity
from core.apps.clients.services.client import BaseClientService
from core.apps.clients.services.client_auth import BaseClientAuthService
from core.apps.clients.services.issuedjwttoken import BaseIssuedJwtTokenService
from core.apps.common.authentication.token import BaseTokenService


@dataclass
class LoginClientUseCase:
    client_service: BaseClientService
    client_auth_service: BaseClientAuthService
    issued_jwt_token_service: BaseIssuedJwtTokenService
    token_service: BaseTokenService

    def execute(self, email: str, password: str) -> tuple[ClientEntity, TokenEntity]:
        client = self.client_service.get_by_email(client_email=email)
        self.client_auth_service.validate_password(email=email, plain_password=password)

        tokens: TokenEntity = self.client_auth_service.generate_tokens(client=client)
        raw_tokens = [self.token_service.decode_token(token) for token in [tokens.access_token, tokens.refresh_token]]
        self.issued_jwt_token_service.bulk_create(subject=client, raw_tokens=raw_tokens)

        return client, tokens
