from dataclasses import dataclass

from core.apps.clients.entities.token import Token as TokenEntity
from core.apps.clients.exceptions.issuedjwttoken import ClientTokensRevokedException
from core.apps.clients.services.client import BaseClientService
from core.apps.clients.services.client_auth import BaseClientAuthService
from core.apps.clients.services.issuedjwttoken import BaseIssuedJwtTokenService
from core.apps.common.authentication.token import BaseTokenService
from core.apps.common.exceptions import InvalidTokenTypeException
from core.apps.common.models import TokenType


@dataclass
class UpdateAccessTokenUseCase:
    client_service: BaseClientService
    client_auth_service: BaseClientAuthService
    issued_jwt_token_service: BaseIssuedJwtTokenService
    token_service: BaseTokenService

    def execute(self, refresh_token: str) -> TokenEntity:
        if self.token_service.get_token_type_from_token(token=refresh_token) != TokenType.REFRESH:
            raise InvalidTokenTypeException

        client_email = self.token_service.get_client_email_from_token(token=refresh_token)
        client = self.client_service.get_by_email(client_email=client_email)

        refresh_jti = self.token_service.get_jti_from_token(token=refresh_token)
        if self.issued_jwt_token_service.check_revoked(jti=refresh_jti):
            self.issued_jwt_token_service.revoke_client_tokens(subject=client)
            raise ClientTokensRevokedException(client_email=client.email)

        device_id = self.token_service.get_device_id_from_token(token=refresh_token)
        new_tokens: TokenEntity = self.client_auth_service.update_access_token(client=client, device_id=device_id)
        self.issued_jwt_token_service.create(
            subject=client,
            jti=self.token_service.get_jti_from_token(token=new_tokens.access_token),
            device_id=self.token_service.get_device_id_from_token(token=new_tokens.access_token),
            expiration_time=self.token_service.get_expiration_time_from_token(token=new_tokens.access_token),
        )
        return new_tokens
