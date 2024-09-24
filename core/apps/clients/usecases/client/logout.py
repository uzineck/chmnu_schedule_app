from dataclasses import dataclass

from core.apps.clients.services.client import BaseClientService
from core.apps.clients.services.issuedjwttoken import BaseIssuedJwtTokenService


@dataclass
class LogoutClientUseCase:
    client_service: BaseClientService
    issued_jwt_token_service: BaseIssuedJwtTokenService

    def execute(self, token: str) -> None:
        client_email = self.client_service.get_client_email_from_token(token=token)
        client = self.client_service.get_by_email(email=client_email)
        device_id = self.client_service.get_device_id_from_token(token=token)
        self.issued_jwt_token_service.revoke_client_device_tokens(subject=client, device_id=device_id)
