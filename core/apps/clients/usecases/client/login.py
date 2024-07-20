from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.services.client import BaseClientService


@dataclass
class LoginClientUseCase:
    client_service: BaseClientService

    def execute(self, email: str, password: str) -> tuple[ClientEntity, str]:
        client = self.client_service.validate_user(email=email, password=password)
        return client, self.client_service.generate_token(client=client)
