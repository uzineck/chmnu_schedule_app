from dataclasses import dataclass

from core.apps.clients.services.client import BaseClientService
from core.apps.common.models import ClientRole
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.services.groups import BaseGroupService
from core.apps.schedule.validators.group import BaseGroupValidatorService


@dataclass
class CreateGroupUseCase:
    client_service: BaseClientService
    group_service: BaseGroupService

    group_validator_service: BaseGroupValidatorService

    def execute(self, group_number: str, headman_email: str, has_subgroups: bool) -> GroupEntity:
        headman = self.client_service.get_by_email(email=headman_email)
        self.client_service.check_user_role(user_role=headman.role, required_role=ClientRole.HEADMAN)
        self.group_validator_service.validate(group_number=group_number, headman=headman)

        return self.group_service.create(
            group_number=group_number,
            has_subgroups=has_subgroups,
            headman_id=headman.id,
        )




