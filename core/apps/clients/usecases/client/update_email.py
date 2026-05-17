from django.db import transaction

from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.entities.token import Token as TokenEntity
from core.apps.clients.services.client import BaseClientService
from core.apps.clients.services.client_auth import BaseClientAuthService
from core.apps.clients.services.issuedjwttoken import BaseIssuedJwtTokenService
from core.apps.common.authentication.token import BaseTokenService
from core.apps.common.authentication.validators.email import BaseEmailValidatorService
from core.apps.common.cache.decorator import cache_decorator


@dataclass
class UpdateClientEmailUseCase:
    client_service: BaseClientService
    client_auth_service: BaseClientAuthService
    issued_jwt_token_service: BaseIssuedJwtTokenService
    token_service: BaseTokenService

    email_validator_service: BaseEmailValidatorService

    @cache_decorator.delete_caches([
        dict(model_prefix='group', identifier=lambda kw: kw['old_email'], func_prefix='*'),
        dict(model_prefix='client', identifier=lambda kw: kw['old_email'], func_prefix='*'),
    ])
    def execute(self, old_email: str, new_email: str, password: str) -> tuple[ClientEntity, TokenEntity]:
        client = self.client_service.get_by_email(client_email=old_email)
        self.client_auth_service.validate_password(email=old_email, plain_password=password)

        self.email_validator_service.validate(email=new_email, old_email=old_email)

        tokens: TokenEntity = self.client_auth_service.generate_tokens(client=client)
        raw_tokens = [self.token_service.decode_token(token) for token in [tokens.access_token, tokens.refresh_token]]

        with transaction.atomic():
            self.client_service.update_email(client_id=client.id, email=new_email)
            self.issued_jwt_token_service.revoke_client_tokens(subject=client)
            self.issued_jwt_token_service.bulk_create(subject=client, raw_tokens=raw_tokens)

        updated_client = self.client_service.get_by_id(client_id=client.id)
        return updated_client, tokens
