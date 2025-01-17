from dataclasses import dataclass

from core.apps.clients.services.client import BaseClientService
from core.apps.common.models import ClientRole
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.services.faculty import BaseFacultyService
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.validators.group import BaseGroupValidatorService


@dataclass
class CreateGroupUseCase:
    client_service: BaseClientService
    group_service: BaseGroupService
    faculty_service: BaseFacultyService

    group_validator_service: BaseGroupValidatorService

    def execute(self, group_number: str, faculty_uuid: str, headman_email: str, has_subgroups: bool) -> GroupEntity:
        client = self.client_service.get_by_email(client_email=headman_email)
        self.client_service.check_client_role(client_roles=client.roles, required_role=ClientRole.HEADMAN)

        faculty = self.faculty_service.get_by_uuid(faculty_uuid=faculty_uuid)

        self.group_validator_service.validate(group_number=group_number, headman=client)

        group = self.group_service.create(
            group_number=group_number,
            faculty_id=faculty.id,
            has_subgroups=has_subgroups,
            headman_id=client.id,
        )

        return group
