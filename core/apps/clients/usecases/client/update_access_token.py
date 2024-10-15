from dataclasses import dataclass

from core.apps.clients.entities.token import Token as TokenEntity
from core.apps.clients.exceptions.issuedjwttoken import ClientTokensRevokedException
from core.apps.clients.services.client import BaseClientService
from core.apps.clients.services.issuedjwttoken import BaseIssuedJwtTokenService
from core.apps.common.exceptions import InvalidTokenTypeException
from core.apps.common.models import TokenType


@dataclass
class UpdateAccessTokenUseCase:
    client_service: BaseClientService
    issued_jwt_token_service: BaseIssuedJwtTokenService

    def execute(self, token: str) -> TokenEntity:
        token_type = self.client_service.get_token_type_from_token(token=token)
        if token_type != TokenType.REFRESH:
            raise InvalidTokenTypeException

        client_email = self.client_service.get_client_email_from_token(token=token)
        client = self.client_service.get_by_email(client_email=client_email)

        if self.issued_jwt_token_service.check_revoked(jti=self.client_service.get_jti_from_token(token=token)):
            self.issued_jwt_token_service.revoke_client_tokens(subject=client)
            raise ClientTokensRevokedException(client_email=client.email)

        device_id = self.client_service.get_device_id_from_token(token=token)
        token: TokenEntity = self.client_service.update_access_token(client=client, device_id=device_id)
        self.issued_jwt_token_service.create(
            subject=client,
            jti=self.client_service.get_jti_from_token(token=token.access_token),
            device_id=self.client_service.get_device_id_from_token(token=token.access_token),
            expiration_time=self.client_service.get_expiration_time_from_token(token=token.access_token),
        )
        return token
