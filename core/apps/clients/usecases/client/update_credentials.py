from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.services.client import BaseClientService
from core.apps.common.cache.decorator import cache_decorator


@dataclass
class UpdateClientCredentialsUseCase:
    client_service: BaseClientService

    @cache_decorator.delete_caches([
        dict(model_prefix='group', identifier=lambda kw: kw['email'], func_prefix='*'),
        dict(model_prefix='client', identifier=lambda kw: kw['email'], func_prefix='*'),
    ])
    def execute(self, email: str, first_name: str, last_name: str, middle_name: str) -> ClientEntity:
        client = self.client_service.get_by_email(client_email=email)
        self.client_service.update_credentials(
            client_id=client.id,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
        )
        updated_client = self.client_service.get_by_id(client_id=client.id)

        return updated_client
