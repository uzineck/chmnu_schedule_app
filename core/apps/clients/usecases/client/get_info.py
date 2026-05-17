from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.services.client import BaseClientService
from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.cache.timeouts import Timeout


@dataclass
class GetClientInfoUseCase:
    client_service: BaseClientService

    @cache_decorator.get_or_set_cache(
        model_prefix='client',
        identifier=lambda kw: kw['email'],
        func_prefix='info',
        timeout=Timeout.WEEK,
    )
    def execute(self, email: str) -> ClientEntity:
        client = self.client_service.get_by_email(client_email=email)

        return client
