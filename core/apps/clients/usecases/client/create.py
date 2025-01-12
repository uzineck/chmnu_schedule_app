from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.services.client import BaseClientService
from core.apps.clients.services.role import BaseRoleService
from core.apps.common.authentication.password import BasePasswordService
from core.apps.common.authentication.validators.email import BaseEmailValidatorService
from core.apps.common.authentication.validators.password import BasePasswordValidatorService


@dataclass
class CreateClientUseCase:
    client_service: BaseClientService
    role_service: BaseRoleService
    password_service: BasePasswordService

    password_validator_service: BasePasswordValidatorService
    email_validator_service: BaseEmailValidatorService

    def execute(
        self,
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

        hashed_password = self.password_service.hash_password(plain_password=password)
        client = self.client_service.create(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            email=email,
            hashed_password=hashed_password,
        )
        fetched_roles = self.role_service.fetch_roles(roles=roles)
        self.client_service.update_roles(client_id=client.id, roles=fetched_roles)
        updated_client = self.client_service.get_by_id(client_id=client.id)

        return updated_client
