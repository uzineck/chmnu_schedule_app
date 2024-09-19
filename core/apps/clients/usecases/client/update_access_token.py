from dataclasses import dataclass

from core.apps.clients.services.client import BaseClientService
from core.apps.common.exceptions import InvalidTokenTypeException
from core.apps.common.models import TokenType


@dataclass
class UpdateAccessTokenUseCase:
    client_service: BaseClientService

    def execute(self, token: str, client_email: str) -> str:
        token_type = self.client_service.get_token_type_from_token(token=token)
        if token_type != TokenType.REFRESH:
            raise InvalidTokenTypeException

        client = self.client_service.get_by_email(email=client_email)

        return self.client_service.update_access_token(client=client)






