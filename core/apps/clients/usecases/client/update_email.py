from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.services.client import BaseClientService
from core.apps.common.authentication.validators.email import BaseEmailValidatorService


@dataclass
class UpdateClientEmailUseCase:
    client_service: BaseClientService
    email_validator_service: BaseEmailValidatorService

    def execute(self, old_email: str, new_email: str, password: str) -> tuple[ClientEntity, str]:
        client = self.client_service.validate_user(email=old_email, password=password)

        self.email_validator_service.validate(email=new_email)

        updated_client = self.client_service.update_email(client=client, email=new_email)

        return updated_client, self.client_service.generate_token(client=updated_client)



