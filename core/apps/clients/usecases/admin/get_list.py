from collections.abc import Iterable
from dataclasses import dataclass

from core.api.filters import PaginationIn
from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.filters.client import ClientSearchFilter
from core.apps.clients.services.client import BaseClientService
from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.cache.timeouts import Timeout


@dataclass
class GetClientListUseCase:
    client_service: BaseClientService

    @cache_decorator.get_or_set_cache(model_prefix='client', func_prefix='list', timeout=Timeout.WEEK)
    def execute(
            self,
            filters: ClientSearchFilter,
            pagination_in: PaginationIn,
    ) -> tuple[Iterable[ClientEntity], int]:
        client_list = self.client_service.get_list(filters=filters, pagination=pagination_in)
        client_count = self.client_service.get_count(filters=filters)

        return client_list, client_count
