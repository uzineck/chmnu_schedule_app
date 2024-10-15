from dataclasses import dataclass

from core.apps.clients.services.client import BaseClientService
from core.apps.common.authentication.password import BasePasswordService
from core.apps.common.authentication.validators.password import BasePasswordValidatorService


@dataclass
class UpdateClientPasswordUseCase:
    client_service: BaseClientService
    password_service: BasePasswordService

    password_validator_service: BasePasswordValidatorService

    def execute(self, email: str, old_password: str, new_password: str, verify_password: str) -> None:
        client = self.client_service.get_by_email(client_email=email)
        self.client_service.validate_password(client_password=client.password, plain_password=old_password)
        self.password_validator_service.validate(
            password=new_password,
            verify_password=verify_password,
            old_password=old_password,
        )
        hashed_password = self.password_service.hash_password(plain_password=new_password)

        self.client_service.update_password(client_id=client.id, hashed_password=hashed_password)
