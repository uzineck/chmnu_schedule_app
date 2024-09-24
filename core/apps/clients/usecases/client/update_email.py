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
        client = self.client_service.validate_client(email=old_email, password=password)
        self.email_validator_service.validate(email=new_email, old_email=old_email)
        updated_client = self.client_service.update_email(client=client, email=new_email)

        tokens: TokenEntity = self.client_service.generate_tokens(client=updated_client)
        self.issued_jwt_token_service.create(
            subject=updated_client,
            jti=self.client_service.get_jti_from_token(token=tokens.refresh_token),
            device_id=self.client_service.get_device_id_from_token(token=tokens.refresh_token),
            expiration_time=self.client_service.get_expiration_time_from_token(token=tokens.refresh_token),
        )

        return updated_client, tokens
