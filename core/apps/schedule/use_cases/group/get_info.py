from dataclasses import dataclass

from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class GetGroupInfoUseCase:
    group_service: BaseGroupService

    uuid_validator_service: BaseUuidValidatorService

    def execute(self, group_uuid: str) -> GroupEntity:
        self.uuid_validator_service.validate(uuid_str=group_uuid)

        return self.group_service.get_by_uuid(group_uuid=group_uuid)
