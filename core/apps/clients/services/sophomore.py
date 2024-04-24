from django.db.utils import IntegrityError

from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.clients.entities.sophomore import Sophomore as SophomoreEntity
from core.apps.clients.exceptions.auth import InvalidAuthDataException
from core.apps.clients.exceptions.sophomores import (
    SophomoreAlreadyExistsException,
    SophomoreEmailNotFoundException,
)
from core.apps.clients.models.sophomors import Sophomore as SophomoreModel
from core.apps.common.authentication.password import BasePasswordService
from core.apps.common.authentication.token import BaseTokenService


@dataclass(eq=False)
class BaseSophomoreService(ABC):
    password_service: BasePasswordService
    token_service: BaseTokenService

    @abstractmethod
    def create(
        self,
        first_name: str,
        last_name: str,
        middle_name: str,
        email: str,
        password: str,
    ) -> SophomoreEntity:
        ...

    @abstractmethod
    def update_password(self, sophomore: SophomoreEntity, plain_password: str) -> SophomoreEntity:
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


class ORMSophomoreService(BaseSophomoreService):
    def create(
        self,
        first_name: str,
        last_name: str,
        middle_name: str,
        email: str,
        password: str,
    ) -> SophomoreEntity:
        hashed_password = self.password_service.hash_password(plain_password=password)
        try:
            sophomore: SophomoreModel = SophomoreModel.objects.create(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                email=email,
                password=hashed_password,
            )
            return sophomore.to_entity()
        except IntegrityError:
            raise SophomoreAlreadyExistsException(email=email)

    def update_password(self, sophomore: SophomoreEntity, plain_password: str) -> SophomoreEntity:
        hashed_password = self.password_service.hash_password(plain_password=plain_password)
        SophomoreModel.objects.filter(email=sophomore.email).update(password=hashed_password)
        updated_sophomore = SophomoreModel.objects.get(email=sophomore.email)
        return updated_sophomore.to_entity()

    def update_email(self, sophomore: SophomoreEntity, email: str) -> SophomoreEntity:
        SophomoreModel.objects.filter(email=sophomore.email).update(email=email)
        try:
            updated_sophomore = SophomoreModel.objects.get(email=email)
        except SophomoreModel.DoesNotExist:
            raise SophomoreEmailNotFoundException(email=email)
        return updated_sophomore.to_entity()

    def update_credentials(
        self,
        sophomore: SophomoreEntity,
        first_name: str,
        last_name: str,
        middle_name: str,
    ) -> SophomoreEntity:
        SophomoreModel.objects.filter(email=sophomore.email).update(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
        )
        updated_sophomore = SophomoreModel.objects.get(email=sophomore.email)
        return updated_sophomore.to_entity()

    def get_by_email(self, email: str) -> SophomoreEntity:
        try:
            sophomore: SophomoreModel = SophomoreModel.objects.get(email=email)
            return sophomore.to_entity()
        except SophomoreModel.DoesNotExist:
            raise SophomoreEmailNotFoundException(email=email)

    def generate_token(self, sophomore: SophomoreEntity) -> str:
        jwt = self.token_service.create_token(sophomore=sophomore)
        SophomoreModel.objects.filter(email=sophomore.email).update(token=jwt)
        return jwt

    def validate_user(self, email: str, password: str) -> SophomoreEntity:
        try:
            sophomore = SophomoreModel.objects.get(email=email)
        except SophomoreModel.DoesNotExist:
            raise InvalidAuthDataException(email=email)

        if not self.password_service.verify_password(plain_password=password, hashed_password=sophomore.password):
            raise InvalidAuthDataException(email=email)

        return sophomore.to_entity()

    def get_user_email_from_token(self, token: str) -> str:
        return self.token_service.get_user_email_from_token(token=token)

    def get_user_id_from_token(self, token: str) -> int:
        return self.token_service.get_user_id_from_token(token=token)
