from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.entities.token import Token as TokenEntity
from core.apps.clients.services.client import BaseClientService
from core.apps.clients.services.issuedjwttoken import BaseIssuedJwtTokenService
from core.apps.common.authentication.validators.email import BaseEmailValidatorService


@dataclass
class UpdateClientEmailUseCase:
    client_service: BaseClientService
    issued_jwt_token_service: BaseIssuedJwtTokenService

    email_validator_service: BaseEmailValidatorService

    def execute(self, old_email: str, new_email: str, password: str) -> tuple[ClientEntity, TokenEntity]:
        client = self.client_service.get_by_email(client_email=old_email)
        self.client_service.validate_password(client_password=client.password, plain_password=password)

        self.email_validator_service.validate(email=new_email, old_email=old_email)

        self.client_service.update_email(client_id=client.id, email=new_email)
        updated_client = self.client_service.get_by_id(client_id=client.id)

        self.issued_jwt_token_service.revoke_client_tokens(subject=client)

        tokens: TokenEntity = self.client_service.generate_tokens(client=updated_client)
        raw_tokens = [self.client_service.get_raw_jwt(token) for token in [tokens.access_token, tokens.refresh_token]]
        self.issued_jwt_token_service.bulk_create(subject=updated_client, raw_tokens=raw_tokens)

        return updated_client, tokens
