from dataclasses import dataclass

from core.apps.clients.entities.client import Sophomore as SophomoreEntity
from core.apps.clients.services.client import BaseClientService
from core.apps.common.authentication.password import BasePasswordService


@dataclass
class CreateClientUseCase:
    client_service: BaseClientService
    password_service: BasePasswordService

    def execute(
        self,
        first_name: str,
        last_name: str,
        middle_name: str,
        email: str,
        password: str,
    ) -> SophomoreEntity:
        hashed_password = self.password_service.hash_password(plain_password=password)
        return self.client_service.create(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            email=email,
            hashed_password=hashed_password,
        )


