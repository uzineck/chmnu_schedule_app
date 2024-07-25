from django.db.utils import IntegrityError

from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.exceptions.auth import InvalidAuthDataException
from core.apps.clients.exceptions.client import (
    ClientAlreadyExistsException,
    ClientEmailNotFoundException,
    ClientRoleNotMatchingWithRequired,
)
from core.apps.clients.models.client import Client as ClientModel
from core.apps.common.authentication.password import BasePasswordService
from core.apps.common.authentication.token import BaseTokenService


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
    def update_password(self, client: ClientEntity, hashed_password: str) -> ClientEntity:
        ...

    @abstractmethod
    def update_email(self, client: ClientEntity, email: str) -> ClientEntity:
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
            new_role: str,
    ) -> ClientEntity:
        ...

    @abstractmethod
    def get_by_email(self, email: str) -> ClientEntity:
        ...

    @abstractmethod
    def generate_token(self, client: ClientEntity) -> str:
        ...

    @abstractmethod
    def validate_user(self, email: str, password: str) -> ClientEntity:
        ...

    @abstractmethod
    def get_user_email_from_token(self, token: str) -> str:
        ...

    @abstractmethod
    def get_user_id_from_token(self, token: str) -> int:
        ...

    @abstractmethod
    def check_user_role(self, user_role: str, required_role: str) -> bool:
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

    def update_password(self, client: ClientEntity, hashed_password: str) -> ClientEntity:
        ClientModel.objects.filter(email=client.email).update(password=hashed_password)
        updated_client = ClientModel.objects.get(email=client.email)

        return updated_client.to_entity()

    def update_email(self, client: ClientEntity, email: str) -> ClientEntity:
        ClientModel.objects.filter(email=client.email).update(email=email)
        try:
            updated_client = ClientModel.objects.get(email=email)
        except ClientModel.DoesNotExist:
            raise ClientEmailNotFoundException(email=email)

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
            new_role: str,
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

    def generate_token(self, client: ClientEntity) -> str:
        jwt = self.token_service.create_token(client=client)
        ClientModel.objects.filter(email=client.email).update(token=jwt)
        return jwt

    def validate_user(self, email: str, password: str) -> ClientEntity:
        try:
            client = ClientModel.objects.get(email=email)
        except ClientModel.DoesNotExist:
            raise InvalidAuthDataException(email=email)

        if not self.password_service.verify_password(plain_password=password, hashed_password=client.password):
            raise InvalidAuthDataException(email=email)

        return client.to_entity()

    def get_user_email_from_token(self, token: str) -> str:
        return self.token_service.get_user_email_from_token(token=token)

    def get_user_id_from_token(self, token: str) -> int:
        return self.token_service.get_user_id_from_token(token=token)

    def get_user_role_from_token(self, token: str) -> str:
        return self.token_service.get_user_role_from_token(token=token)

    def check_user_role(self, user_role: str, required_role: str) -> bool:
        if user_role != required_role:
            raise ClientRoleNotMatchingWithRequired(user_role=user_role)

        return True


