from django.db import transaction

from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.services.client import BaseClientService
from core.apps.clients.services.issuedjwttoken import BaseIssuedJwtTokenService
from core.apps.clients.services.role import BaseRoleService
from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.models import ClientRole


@dataclass
class UpdateClientRoleUseCase:
    client_service: BaseClientService
    role_service: BaseRoleService
    issued_jwt_token_service: BaseIssuedJwtTokenService

    @cache_decorator.delete_caches([
        dict(model_prefix='group', identifier=lambda kw: kw['email'], func_prefix='*'),
        dict(model_prefix='client', identifier=lambda kw: kw['email'], func_prefix='*'),
    ])
    def execute(self, email: str, roles: list[ClientRole]) -> ClientEntity:
        client = self.client_service.get_by_email(client_email=email)
        fetched_roles = self.role_service.fetch_roles(roles=roles)
        if len(fetched_roles) != len(roles):
            raise ValueError(f"Unknown role IDs in {roles}")

        with transaction.atomic():
            self.client_service.update_roles(client_id=client.id, roles=fetched_roles)
            self.issued_jwt_token_service.revoke_client_tokens(subject=client)

        return self.client_service.get_by_id(client_id=client.id)
