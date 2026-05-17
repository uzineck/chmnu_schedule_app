from django.db.utils import IntegrityError

from abc import (
    ABC,
    abstractmethod,
)

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.exceptions.client import (
    ClientAlreadyExistsException,
    ClientNotFoundException,
    ClientUpdateException,
)
from core.apps.clients.models.client import Client as ClientModel


class BaseClientService(ABC):
    @abstractmethod
    def create(
        self,
        first_name: str,
        last_name: str,
        middle_name: str,
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
    def update_roles(
            self,
            client_id: int,
            roles: list[str],
    ) -> None:
        ...

    @abstractmethod
    def get_by_email(self, client_email: str) -> ClientEntity:
        ...

    @abstractmethod
    def get_by_id(self, client_id: int) -> ClientEntity:
        ...

    @abstractmethod
    def get_password_hash_by_email(self, client_email: str) -> str:
        ...

    @abstractmethod
    def check_client_exists(self, client_email: str) -> bool:
        ...


class ORMClientService(BaseClientService):
    def create(
        self,
        first_name: str,
        last_name: str,
        middle_name: str,
        email: str,
        hashed_password: str,
    ) -> ClientEntity:
        try:
            client: ClientModel = ClientModel.objects.create(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                email=email,
                password=hashed_password,
            )
        except IntegrityError:
            raise ClientAlreadyExistsException(email=email)

        return client.to_entity()

    def update_email(self, client_id: int, email: str) -> None:
        is_updated = ClientModel.objects.filter(id=client_id).update(email=email)
        if not is_updated:
            raise ClientUpdateException(id=client_id, email=email)

    def update_password(self, client_id: int, hashed_password: str) -> None:
        is_updated = ClientModel.objects.filter(id=client_id).update(password=hashed_password)
        if not is_updated:
            raise ClientUpdateException(id=client_id)

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
            raise ClientUpdateException(id=client_id)

    def update_roles(
            self,
            client_id: int,
            roles: list[str],
    ) -> None:
        try:
            client: ClientModel = ClientModel.objects.get(id=client_id)
            client.roles.set(roles)
        except (ClientModel.DoesNotExist, IntegrityError):
            raise ClientUpdateException(id=client_id)

    def get_by_email(self, client_email: str) -> ClientEntity:
        try:
            client: ClientModel = ClientModel.objects.get(email=client_email)
        except ClientModel.DoesNotExist:
            raise ClientNotFoundException(email=client_email)

        return client.to_entity()

    def get_by_id(self, client_id: int) -> ClientEntity:
        try:
            client: ClientModel = ClientModel.objects.get(id=client_id)
        except ClientModel.DoesNotExist:
            raise ClientNotFoundException(id=client_id)

        return client.to_entity()

    def get_password_hash_by_email(self, client_email: str) -> str:
        hash_ = (
            ClientModel.objects
            .filter(email=client_email)
            .values_list('password', flat=True)
            .first()
        )
        if hash_ is None:
            raise ClientNotFoundException(email=client_email)
        return hash_

    def check_client_exists(self, client_email: str) -> bool:
        return ClientModel.objects.filter(email=client_email).exists()
