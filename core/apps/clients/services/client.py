from django.db.utils import IntegrityError

import logging
from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import Any

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.entities.token import Token as TokenEntity
from core.apps.clients.exceptions.auth import InvalidAuthDataException
from core.apps.clients.exceptions.client import (
    ClientAlreadyExistsException,
    ClientNotFoundException,
    ClientRoleNotMatchingWithRequiredException,
    ClientUpdateException,
)
from core.apps.clients.models.client import Client as ClientModel
from core.apps.common.authentication.password import BasePasswordService
from core.apps.common.authentication.token import BaseTokenService
from core.apps.common.factory import get_new_uuid
from core.apps.common.models import (
    ClientRole,
    TokenType,
)


logger = logging.getLogger(__name__)


@dataclass(eq=False)
class BaseClientService(ABC):
    password_service: BasePasswordService
    token_service: BaseTokenService

    @abstractmethod
    def create(
        self,
        first_name: str,
        last_name: str,
        middle_name: str,
        role: str,
        email: str,
        hashed_password: str,
    ) -> ClientEntity:
        ...

    @abstractmethod
    def update_email(self, client_id: int, email: str) -> None:
        ...

    @abstractmethod
    def update_password(self, client_id: int, hashed_password: str) -> None:
        ...

    @abstractmethod
    def update_credentials(
        self,
        client_id: int,
        first_name: str,
        last_name: str,
        middle_name: str,
    ) -> None:
        ...

    @abstractmethod
    def update_role(
            self,
            client_id: int,
            new_role: ClientRole,
    ) -> None:
        ...

    @abstractmethod
    def get_by_email(self, client_email: str) -> ClientEntity:
        ...

    @abstractmethod
    def get_by_id(self, client_id: int) -> ClientEntity:
        ...

    @abstractmethod
    def check_client_exists(self, client_email: str) -> bool:
        ...

    @abstractmethod
    def validate_password(self, client_password: str, plain_password: str) -> None:
        ...

    @abstractmethod
    def check_client_role(self, client_role: ClientRole, required_role: ClientRole) -> None:
        ...

    @abstractmethod
    def generate_tokens(self, client: ClientEntity) -> TokenEntity:
        ...

    @abstractmethod
    def update_access_token(self, client: ClientEntity, device_id: str) -> TokenEntity:
        ...

    @abstractmethod
    def get_raw_jwt(self, token: str) -> dict[str, Any]:
        ...

    @abstractmethod
    def get_client_email_from_token(self, token: str) -> str:
        ...

    @abstractmethod
    def get_client_role_from_token(self, token: str) -> str:
        ...

    @abstractmethod
    def get_token_type_from_token(self, token: str) -> TokenType:
        ...

    @abstractmethod
    def get_jti_from_token(self, token: str) -> str:
        ...

    @abstractmethod
    def get_device_id_from_token(self, token: str) -> str:
        ...

    @abstractmethod
    def get_expiration_time_from_token(self, token: str) -> int:
        ...


class ORMClientService(BaseClientService):
    def create(
        self,
        first_name: str,
        last_name: str,
        middle_name: str,
        role: str,
        email: str,
        hashed_password: str,
    ) -> ClientEntity:
        try:
            client: ClientModel = ClientModel.objects.create(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                role=role,
                email=email,
                password=hashed_password,
            )
        except IntegrityError:
            logger.warning(f"Client Creation Error ({email=}, {role=})")
            raise ClientAlreadyExistsException(email=email)

        return client.to_entity()

    def update_email(self, client_id: int, email: str) -> None:
        is_updated = ClientModel.objects.filter(id=client_id).update(email=email)
        if not is_updated:
            logger.error(f"Client Update Email Error ({client_id=}, {email=})")
            raise ClientUpdateException(id=client_id, email=email)

    def update_password(self, client_id: int, hashed_password: str) -> None:
        is_updated = ClientModel.objects.filter(id=client_id).update(password=hashed_password)
        if not is_updated:
            logger.error(f"Client Update Password Error ({client_id=})")
            raise ClientUpdateException(id=client_id, password=hashed_password)

    def update_credentials(
        self,
        client_id: int,
        first_name: str,
        last_name: str,
        middle_name: str,
    ) -> None:
        is_updated = ClientModel.objects.filter(id=client_id).update(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
        )
        if not is_updated:
            logger.error(f"Client Update Credentials Error ({client_id=})")
            raise ClientUpdateException(id=client_id)

    def update_role(
            self,
            client_id: int,
            new_role: ClientRole,
    ) -> None:
        is_updated = ClientModel.objects.filter(id=client_id).update(
            role=new_role,
        )
        if not is_updated:
            logger.error(f"Client Update Role Error ({client_id=}, {new_role=})")
            raise ClientUpdateException(id=client_id)

    def get_by_email(self, client_email: str) -> ClientEntity:
        try:
            client: ClientModel = ClientModel.objects.get(email=client_email)
        except ClientModel.DoesNotExist:
            logger.info(f"Client Does Not Exist Error ({client_email=})")
            raise ClientNotFoundException(email=client_email)

        return client.to_entity()

    def get_by_id(self, client_id: int) -> ClientEntity:
        try:
            client: ClientModel = ClientModel.objects.get(id=client_id)
        except ClientModel.DoesNotExist:
            logger.error(f"Client Does Not Exist Error ({client_id=})")
            raise ClientNotFoundException(id=client_id)

        return client.to_entity()

    def check_client_exists(self, client_email: str) -> bool:
        return ClientModel.objects.filter(email=client_email).exists()

    def validate_password(self, client_password: str, plain_password: str) -> None:
        if not self.password_service.verify_password(plain_password=plain_password, hashed_password=client_password):
            logger.info("Client Validate Password Error")
            raise InvalidAuthDataException

    def check_client_role(self, client_role: str, required_role: ClientRole) -> None:
        if client_role != required_role:
            logger.warning(f"Client Role Not Matching Error ({client_role=}, {required_role=})")
            raise ClientRoleNotMatchingWithRequiredException(client_role=client_role, required_role=required_role)

    def generate_tokens(self, client: ClientEntity) -> TokenEntity:
        device_id = get_new_uuid()
        access_token = self.token_service.create_access_token(client=client, payload={"device_id": device_id})
        refresh_token = self.token_service.create_refresh_token(client=client, payload={"device_id": device_id})

        return TokenEntity(access_token=access_token, refresh_token=refresh_token)

    def update_access_token(self, client: ClientEntity, device_id: str) -> TokenEntity:
        access_token = self.token_service.create_access_token(client=client, payload={"device_id": device_id})

        return TokenEntity(access_token=access_token)

    def get_raw_jwt(self, token: str) -> dict[str, Any]:
        payload = self.token_service.get_raw_jwt(token=token)

        return payload

    def get_client_email_from_token(self, token: str) -> str:
        return self.token_service.get_client_email_from_token(token=token)

    def get_client_role_from_token(self, token: str) -> str:
        return self.token_service.get_client_role_from_token(token=token)

    def get_token_type_from_token(self, token: str) -> TokenType:
        return self.token_service.get_token_type_from_token(token=token)

    def get_jti_from_token(self, token: str) -> str:
        return self.token_service.get_jti_from_token(token=token)

    def get_device_id_from_token(self, token: str) -> str:
        return self.token_service.get_device_id_from_token(token=token)

    def get_expiration_time_from_token(self, token: str) -> int:
        return self.token_service.get_expiration_time_from_token(token=token)
