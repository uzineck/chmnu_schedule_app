from dataclasses import dataclass

from core.apps.clients.services.client import BaseClientService
from core.apps.clients.services.client_auth import BaseClientAuthService
from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.cache.timeouts import Timeout
from core.apps.common.models import ClientRole
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.services.group import BaseGroupService


@dataclass
class GetHeadmanGroupUseCase:
    client_service: BaseClientService
    client_auth_service: BaseClientAuthService
    group_service: BaseGroupService

    @cache_decorator.get_or_set_cache(
        model_prefix='group',
        identifier=lambda kw: kw['email'],
        func_prefix='group',
        timeout=Timeout.DAY,
    )
    def execute(self, email: str) -> GroupEntity:
        client = self.client_service.get_by_email(client_email=email)
        self.client_auth_service.check_client_role(client_roles=client.roles, required_role=ClientRole.HEADMAN)
        group = self.group_service.get_group_from_headman(headman_id=client.id)
        return group
