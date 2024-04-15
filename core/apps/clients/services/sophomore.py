from dataclasses import dataclass
from uuid import uuid4
from abc import ABC, abstractmethod

from core.apps.clients.entities.sophomore import Sophomore as SophomoreEntity
from core.apps.clients.models.sophomors import Sophomore as SophomoreModel
from core.apps.common.authentication import BaseAuthenticationService
from core.apps.clients.exceptions.sophomores import SophomoreEmailException


@dataclass(eq=False)
class BaseSophomoreService(ABC):
    auth_service: BaseAuthenticationService

    @abstractmethod
    def create(self,
               first_name: str,
               last_name: str,
               middle_name: str,
               email: str,
               password: str):
        ...

    @abstractmethod
    def update_password(self, sophomore: SophomoreEntity, plain_password: str):
        ...

    @abstractmethod
    def update_email(self, sophomore: SophomoreEntity, email: str):
        ...

    @abstractmethod
    def get_by_email(self, email: str) -> SophomoreEntity:
        ...


class ORMSophomoreService(BaseSophomoreService):
    def create(self,
               first_name: str,
               last_name: str,
               middle_name: str,
               email: str,
               password: str):
        hashed_password = self.auth_service.hash_password(plain_password=password)
        sophomore: SophomoreModel = SophomoreModel.objects.create(first_name=first_name,
                                                                  last_name=last_name,
                                                                  middle_name=middle_name,
                                                                  email=email,
                                                                  password=hashed_password)
        return sophomore.to_entity()

    def update_password(self, sophomore: SophomoreEntity, plain_password: str):
        hashed_password = self.auth_service.hash_password(plain_password=plain_password)
        SophomoreModel.objects.filter(email=sophomore.email).update(password=hashed_password)
        return hashed_password

    def update_email(self, sophomore: SophomoreEntity, email: str):
        SophomoreModel.objects.filter(email=sophomore.email).update(email=email)
        return email

    def get_by_email(self, email: str) -> SophomoreEntity:
        try:
            sophomore: SophomoreModel = SophomoreModel.objects.get(email=email)
            return sophomore.to_entity()
        except SophomoreModel.DoesNotExist:
            raise SophomoreEmailException
