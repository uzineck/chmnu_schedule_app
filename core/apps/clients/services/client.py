from django.db.utils import IntegrityError

from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.clients.entities.client import Sophomore as SophomoreEntity
from core.apps.clients.exceptions.auth import InvalidAuthDataException
from core.apps.clients.exceptions.client import (
    ClientAlreadyExistsException,
    ClientEmailNotFoundException,
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
        email: str,
        hashed_password: str,
    ) -> SophomoreEntity:
        ...

    @abstractmethod
    def update_password(self, sophomore: SophomoreEntity, hashed_password: str) -> SophomoreEntity:
        ...

    @abstractmethod
    def update_email(self, sophomore: SophomoreEntity, email: str) -> SophomoreEntity:
        ...

    @abstractmethod
    def update_credentials(
        self, sophomore: SophomoreEntity,
        first_name: str, last_name: str, middle_name: str,
    ) -> SophomoreEntity:
        ...

    @abstractmethod
    def get_by_email(self, email: str) -> SophomoreEntity:
        ...

    @abstractmethod
    def generate_token(self, sophomore: SophomoreEntity) -> str:
        ...

    @abstractmethod
    def validate_user(self, email: str, password: str) -> SophomoreEntity:
        ...

    @abstractmethod
    def get_user_email_from_token(self, token: str) -> str:
        ...

    @abstractmethod
    def get_user_id_from_token(self, token: str) -> int:
        ...


class ORMClientService(BaseClientService):
    def create(
        self,
        first_name: str,
        last_name: str,
        middle_name: str,
        email: str,
        hashed_password: str,
    ) -> SophomoreEntity:
        try:
            sophomore: ClientModel = ClientModel.objects.create(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                email=email,
                password=hashed_password,
            )
        except IntegrityError:
            raise ClientAlreadyExistsException(email=email)

        return sophomore.to_entity()

    def update_password(self, sophomore: SophomoreEntity, hashed_password: str) -> SophomoreEntity:
        ClientModel.objects.filter(email=sophomore.email).update(password=hashed_password)
        updated_sophomore = ClientModel.objects.get(email=sophomore.email)

        return updated_sophomore.to_entity()

    def update_email(self, sophomore: SophomoreEntity, email: str) -> SophomoreEntity:
        ClientModel.objects.filter(email=sophomore.email).update(email=email)
        try:
            updated_sophomore = ClientModel.objects.get(email=email)
        except ClientModel.DoesNotExist:
            raise ClientEmailNotFoundException(email=email)

        return updated_sophomore.to_entity()

    def update_credentials(
        self,
        sophomore: SophomoreEntity,
        first_name: str,
        last_name: str,
        middle_name: str,
    ) -> SophomoreEntity:
        ClientModel.objects.filter(email=sophomore.email).update(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
        )
        updated_sophomore = ClientModel.objects.get(email=sophomore.email)

        return updated_sophomore.to_entity()

    def get_by_email(self, email: str) -> SophomoreEntity:
        try:
            sophomore: ClientModel = ClientModel.objects.get(email=email)
        except ClientModel.DoesNotExist:
            raise ClientEmailNotFoundException(email=email)

        return sophomore.to_entity()

    def generate_token(self, sophomore: SophomoreEntity) -> str:
        jwt = self.token_service.create_token(sophomore=sophomore)
        ClientModel.objects.filter(email=sophomore.email).update(token=jwt)
        return jwt

    def validate_user(self, email: str, password: str) -> SophomoreEntity:
        try:
            sophomore = ClientModel.objects.get(email=email)
        except ClientModel.DoesNotExist:
            raise InvalidAuthDataException(email=email)

        if not self.password_service.verify_password(plain_password=password, hashed_password=sophomore.password):
            raise InvalidAuthDataException(email=email)

        return sophomore.to_entity()

    def get_user_email_from_token(self, token: str) -> str:
        return self.token_service.get_user_email_from_token(token=token)

    def get_user_id_from_token(self, token: str) -> int:
        return self.token_service.get_user_id_from_token(token=token)
