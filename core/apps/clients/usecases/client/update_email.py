from dataclasses import dataclass

from core.apps.clients.entities.client import Sophomore as SophomoreEntity
from core.apps.clients.services.client import BaseClientService
from core.apps.common.authentication.password import BasePasswordService


@dataclass
class UpdateClientEmailUseCase:
    client_service: BaseClientService
    password_service: BasePasswordService

    def execute(self, old_email: str, new_email: str, password: str) -> tuple[SophomoreEntity, str]:
        sophomore = self.client_service.validate_user(email=old_email, password=password)
        updated_sophomore = self.client_service.update_email(sophomore=sophomore, email=new_email)

        return updated_sophomore, self.client_service.generate_token(sophomore=updated_sophomore)



