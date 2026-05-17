from dataclasses import dataclass

from core.apps.clients.services.client import BaseClientService
from core.apps.clients.services.issuedjwttoken import BaseIssuedJwtTokenService


@dataclass
class LogoutClientUseCase:
    client_service: BaseClientService
    issued_jwt_token_service: BaseIssuedJwtTokenService

    def execute(self, client_email: str, device_id: str) -> None:
        client = self.client_service.get_by_email(client_email=client_email)
        self.issued_jwt_token_service.revoke_client_device_tokens(subject=client, device_id=device_id)
