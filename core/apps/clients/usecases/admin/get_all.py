from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.filters.client import ClientSearchFilter
from core.apps.clients.services.client import BaseClientService
from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.cache.timeouts import Timeout


@dataclass
class GetAllClientsUseCase:
    client_service: BaseClientService

    @cache_decorator.get_or_set_cache(model_prefix='client', func_prefix='all', timeout=Timeout.WEEK)
    def execute(self, filters: ClientSearchFilter) -> list[ClientEntity]:
        return list(self.client_service.get_all(filters=filters))
