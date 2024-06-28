from dataclasses import dataclass

from core.apps.clients.entities.client import Sophomore as SophomoreEntity
from core.apps.clients.services.client import BaseClientService


@dataclass
class UpdateClientCredentialsUseCase:
    client_service: BaseClientService

    def execute(self, email: str, first_name: str, last_name: str, middle_name: str) -> SophomoreEntity:
        sophomore = self.client_service.get_by_email(email=email)
        updated_sophomore = self.client_service.update_credentials(
            sophomore=sophomore,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
        )

        return updated_sophomore


