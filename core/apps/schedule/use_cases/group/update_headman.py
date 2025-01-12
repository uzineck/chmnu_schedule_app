from dataclasses import dataclass

from core.apps.clients.services.client import BaseClientService
from core.apps.common.models import ClientRole
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.validators.group import BaseGroupValidatorService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class UpdateGroupHeadmanUseCase:
    client_service: BaseClientService
    group_service: BaseGroupService

    group_validator_service: BaseGroupValidatorService
    uuid_validator_service: BaseUuidValidatorService

    def execute(self, group_uuid: str, new_headman_email: str) -> GroupEntity:
        self.uuid_validator_service.validate(uuid_str=group_uuid)

        group = self.group_service.get_by_uuid(group_uuid=group_uuid)
        client = self.client_service.get_by_email(client_email=new_headman_email)

        self.client_service.check_client_role(client_roles=client.roles, required_role=ClientRole.HEADMAN)
        self.group_validator_service.validate(headman=client)

        self.group_service.update_group_headman(group_id=group.id, headman_id=client.id)
        updated_group = self.group_service.get_by_id(group_id=group.id)

        return updated_group
