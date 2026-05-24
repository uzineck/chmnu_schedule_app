from django.db import transaction

from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.exceptions.client import InsufficientPrivilegeToManageRoleException
from core.apps.clients.services.client import BaseClientService
from core.apps.clients.services.role import BaseRoleService
from core.apps.common.authentication.password import BasePasswordService
from core.apps.common.authentication.validators.email import BaseEmailValidatorService
from core.apps.common.authentication.validators.password import BasePasswordValidatorService
from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.models import ClientRole


CLIENT_MANAGER_ASSIGNABLE_ROLES: frozenset[ClientRole] = frozenset({ClientRole.HEADMAN})


@dataclass
class CreateClientUseCase:
    client_service: BaseClientService
    role_service: BaseRoleService
    password_service: BasePasswordService

    password_validator_service: BasePasswordValidatorService
    email_validator_service: BaseEmailValidatorService

    @cache_decorator.delete_caches([
        dict(model_prefix='client', func_prefix='all', filters='*'),
        dict(model_prefix='client', func_prefix='list', filters='*', pagination_in='*'),
    ])
    def execute(
        self,
        caller_roles: list[ClientRole],
        first_name: str,
        last_name: str,
        middle_name: str,
        roles: list[str],
        email: str,
        password: str,
        verify_password: str,
    ) -> ClientEntity:

        self.email_validator_service.validate(email=email)
        self.password_validator_service.validate(password=password, verify_password=verify_password)

        if ClientRole.ADMIN not in caller_roles:
            target = {ClientRole(r) for r in roles}
            if not target.issubset(CLIENT_MANAGER_ASSIGNABLE_ROLES):
                raise InsufficientPrivilegeToManageRoleException(
                    caller_roles=[r.value for r in caller_roles],
                    target_roles=[r.value for r in target],
                )

        hashed_password = self.password_service.hash_password(plain_password=password)
        fetched_roles = self.role_service.fetch_roles(roles=roles)
        if len(fetched_roles) != len(roles):
            raise ValueError(f"Unknown role IDs in {roles}")

        with transaction.atomic():
            client = self.client_service.create(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                email=email,
                hashed_password=hashed_password,
            )
            self.client_service.update_roles(client_id=client.id, roles=fetched_roles)

        return self.client_service.get_by_id(client_id=client.id)
