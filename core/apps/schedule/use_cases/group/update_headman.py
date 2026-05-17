from dataclasses import dataclass

from core.apps.clients.services.client import BaseClientService
from core.apps.clients.services.client_auth import BaseClientAuthService
from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.models import ClientRole
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.validators.group import BaseGroupValidatorService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class UpdateGroupHeadmanUseCase:
    client_service: BaseClientService
    client_auth_service: BaseClientAuthService
    group_service: BaseGroupService

    group_validator_service: BaseGroupValidatorService
    uuid_validator_service: BaseUuidValidatorService

    @cache_decorator.delete_caches([
        dict(model_prefix='group', identifier=lambda kw: kw['group_uuid'], func_prefix='info'),
        dict(model_prefix='group', identifier=lambda kw: kw['new_headman_email'], func_prefix='group'),
        dict(model_prefix='group', identifier=lambda kw, res: res[1], func_prefix='group'),
    ])
    def execute(self, group_uuid: str, new_headman_email: str) -> tuple[GroupEntity, str | None]:
        self.uuid_validator_service.validate(uuid_str=group_uuid)

        group = self.group_service.get_by_uuid(group_uuid=group_uuid)
        old_headman_email = group.headman.email if group.headman else None
        client = self.client_service.get_by_email(client_email=new_headman_email)

        self.client_auth_service.check_client_role(client_roles=client.roles, required_role=ClientRole.HEADMAN)
        self.group_validator_service.validate(headman=client)

        self.group_service.update_group_headman(group_id=group.id, headman_id=client.id)
        updated_group = self.group_service.get_by_id(group_id=group.id)

        return updated_group, old_headman_email
