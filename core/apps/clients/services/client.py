from django.db.utils import IntegrityError

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
    ClientEmailNotFoundException,
    ClientRoleNotMatchingWithRequired,
)
from core.apps.clients.models.client import Client as ClientModel
from core.apps.common.authentication.password import BasePasswordService
from core.apps.common.authentication.token import BaseTokenService
from core.apps.common.models import (
    ClientRole,
    TokenType,
)


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
    def update_email(self, client: ClientEntity, email: str) -> ClientEntity:
        ...

    @abstractmethod
    def update_password(self, client: ClientEntity, hashed_password: str) -> ClientEntity:
        ...

    @abstractmethod
    def update_credentials(
        self,
        client: ClientEntity,
        first_name: str,
        last_name: str,
        middle_name: str,
    ) -> ClientEntity:
        ...

    @abstractmethod
    def update_role(
            self,
            client: ClientEntity,
            new_role: ClientRole,
    ) -> ClientEntity:
        ...

    @abstractmethod
    def get_by_email(self, email: str) -> ClientEntity:
        ...

    @abstractmethod
    def validate_client(self, email: str, password: str) -> ClientEntity:
        ...

    @abstractmethod
    def check_user_role(self, user_role: ClientRole, required_role: ClientRole) -> None:
        ...

    @abstractmethod
    def generate_tokens(self, client: ClientEntity) -> TokenEntity:
        ...

    @abstractmethod
    def update_access_token(self, client: ClientEntity) -> str:
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
            raise ClientAlreadyExistsException(email=email)

        return client.to_entity()

    def update_email(self, client: ClientEntity, email: str) -> ClientEntity:
        ClientModel.objects.filter(email=client.email).update(email=email)
        try:
            updated_client = ClientModel.objects.get(email=email)
        except ClientModel.DoesNotExist:
            raise ClientEmailNotFoundException(email=email)

        return updated_client.to_entity()

    def update_password(self, client: ClientEntity, hashed_password: str) -> ClientEntity:
        ClientModel.objects.filter(email=client.email).update(password=hashed_password)
        updated_client = ClientModel.objects.get(email=client.email)

        return updated_client.to_entity()

    def update_credentials(
        self,
        client: ClientEntity,
        first_name: str,
        last_name: str,
        middle_name: str,
    ) -> ClientEntity:
        ClientModel.objects.filter(email=client.email).update(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
        )
        updated_client = ClientModel.objects.get(email=client.email)

        return updated_client.to_entity()

    def update_role(
            self,
            client: ClientEntity,
            new_role: ClientRole,
    ) -> ClientEntity:
        ClientModel.objects.filter(email=client.email).update(
            role=new_role,
        )
        updated_client = ClientModel.objects.get(email=client.email)
        return updated_client.to_entity()

    def get_by_email(self, email: str) -> ClientEntity:
        try:
            client: ClientModel = ClientModel.objects.get(email=email)
        except ClientModel.DoesNotExist:
            raise ClientEmailNotFoundException(email=email)

        return client.to_entity()

    def validate_client(self, email: str, password: str) -> ClientEntity:
        try:
            client = ClientModel.objects.get(email=email)
        except ClientModel.DoesNotExist:
            raise InvalidAuthDataException(email=email)

        if not self.password_service.verify_password(plain_password=password, hashed_password=client.password):
            raise InvalidAuthDataException(email=email)

        return client.to_entity()

    def check_user_role(self, user_role: str, required_role: ClientRole) -> None:
        if user_role != required_role:
            raise ClientRoleNotMatchingWithRequired(client_role=user_role)

    def generate_tokens(self, client: ClientEntity) -> TokenEntity:
        jwt_token_entity: TokenEntity = self.token_service.create_tokens(client=client)
        ClientModel.objects.filter(email=client.email).update(
            access_token=jwt_token_entity.access_token,
            refresh_token=jwt_token_entity.refresh_token,
        )
        return jwt_token_entity

    def update_access_token(self, client: ClientEntity) -> str:
        jwt_tokens = self.token_service.create_tokens(client=client)
        ClientModel.objects.filter(email=client.email).update(
            access_token=jwt_tokens.access_token,
        )
        return jwt_tokens.access_token

    def validate_token(self, token: str) -> dict[str, Any]:
        payload = self.token_service.validate_token(token=token)

        return payload

    def get_client_email_from_token(self, token: str) -> str:
        return self.token_service.get_client_email_from_token(token=token)

    def get_client_role_from_token(self, token: str) -> str:
        return self.token_service.get_client_role_from_token(token=token)

    def get_token_type_from_token(self, token: str) -> TokenType:
        return self.token_service.get_token_type_from_token(token=token)



