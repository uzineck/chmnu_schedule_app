from dataclasses import dataclass

from core.apps.clients.entities.client import Sophomore as SophomoreEntity
from core.apps.clients.services.client import BaseClientService


@dataclass
class LoginClientUseCase:
    client_service: BaseClientService

    def execute(self, email: str, password: str) -> tuple[SophomoreEntity, str]:
        sophomore = self.client_service.validate_user(email=email, password=password)
        return sophomore, self.client_service.generate_token(sophomore=sophomore)
