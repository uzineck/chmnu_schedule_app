from django.db import transaction

from dataclasses import dataclass

from core.apps.clients.services.client import BaseClientService
from core.apps.clients.services.client_auth import BaseClientAuthService
from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.models import ClientRole
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.services.faculty import BaseFacultyService
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.validators.group import BaseGroupValidatorService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class CreateGroupUseCase:
    client_service: BaseClientService
    client_auth_service: BaseClientAuthService
    group_service: BaseGroupService
    faculty_service: BaseFacultyService

    group_validator_service: BaseGroupValidatorService
    uuid_validator_service: BaseUuidValidatorService

    @cache_decorator.delete_caches([
        dict(model_prefix='group', func_prefix='all'),
        dict(model_prefix='group', func_prefix='list', filters='*', pagination_in='*'),
    ])
    def execute(self, group_number: str, faculty_uuid: str, headman_email: str, has_subgroups: bool) -> GroupEntity:
        self.uuid_validator_service.validate(uuid_str=faculty_uuid)

        client = self.client_service.get_by_email(client_email=headman_email)
        self.client_auth_service.check_client_role(client_roles=client.roles, required_role=ClientRole.HEADMAN)

        faculty = self.faculty_service.get_by_uuid(faculty_uuid=faculty_uuid)

        self.group_validator_service.validate(group_number=group_number, headman=client)

        existing = self.group_service.find_any_by_number(group_number=group_number)
        if existing is not None and not existing.is_active:
            with transaction.atomic():
                self.group_service.restore(group_id=existing.id)
                self.group_service.update_group_headman(group_id=existing.id, headman_id=client.id)
            return self.group_service.get_by_id(group_id=existing.id)

        return self.group_service.create(
            group_number=group_number,
            faculty_id=faculty.id,
            has_subgroups=has_subgroups,
            headman_id=client.id,
        )
