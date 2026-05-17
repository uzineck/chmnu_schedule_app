from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.entities.token import Token as TokenEntity
from core.apps.clients.exceptions.auth import InvalidAuthDataException
from core.apps.clients.exceptions.client import ClientRoleNotMatchingWithRequiredException
from core.apps.clients.services.client import BaseClientService
from core.apps.common.authentication.password import BasePasswordService
from core.apps.common.authentication.token import BaseTokenService
from core.apps.common.factory import get_new_uuid
from core.apps.common.models import ClientRole


@dataclass(eq=False)
class BaseClientAuthService(ABC):
    password_service: BasePasswordService
    token_service: BaseTokenService
    client_service: BaseClientService

    @abstractmethod
    def validate_password(self, email: str, plain_password: str) -> None:
        ...

    @abstractmethod
    def check_client_role(self, client_roles: list[ClientRole], required_role: ClientRole) -> None:
        ...

    @abstractmethod
    def generate_tokens(self, client: ClientEntity) -> TokenEntity:
        ...

    @abstractmethod
    def update_access_token(self, client: ClientEntity, device_id: str) -> TokenEntity:
        ...


class ORMClientAuthService(BaseClientAuthService):
    def validate_password(self, email: str, plain_password: str) -> None:
        hashed = self.client_service.get_password_hash_by_email(client_email=email)
        if not self.password_service.verify_password(plain_password=plain_password, hashed_password=hashed):
            raise InvalidAuthDataException

    def check_client_role(self, client_roles: list[ClientRole], required_role: ClientRole) -> None:
        if required_role not in client_roles:
            raise ClientRoleNotMatchingWithRequiredException(
                client_roles=client_roles,
                required_role=required_role,
            )

    def generate_tokens(self, client: ClientEntity) -> TokenEntity:
        device_id = get_new_uuid()
        access_token = self.token_service.create_access_token(client=client, payload={"device_id": device_id})
        refresh_token = self.token_service.create_refresh_token(client=client, payload={"device_id": device_id})

        return TokenEntity(access_token=access_token, refresh_token=refresh_token)

    def update_access_token(self, client: ClientEntity, device_id: str) -> TokenEntity:
        access_token = self.token_service.create_access_token(client=client, payload={"device_id": device_id})

        return TokenEntity(access_token=access_token)
