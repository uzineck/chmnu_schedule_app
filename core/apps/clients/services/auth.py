from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.apps.common.authentication import BaseAuthenticationService
from core.apps.clients.services.sophomore import BaseSophomoreService
from core.apps.clients.exceptions.sophomores import SophomoreEmailException
from core.apps.common.exceptions import NotAuthorizedException


@dataclass(eq=False)
class BaseAuthService(ABC):
    authentication_service: BaseAuthenticationService
    client_service: BaseSophomoreService

    @abstractmethod
    def sign_up(self,
                first_name: str,
                last_name: str,
                middle_name: str,
                email: str,
                password: str):
        ...

    @abstractmethod
    def login(self, email: str, password: str):
        ...


class AuthService(BaseAuthService):
    def sign_up(self, first_name: str, last_name: str, middle_name: str, email: str, password: str):
        return self.client_service.create(first_name, last_name, middle_name, email, password)

    def login(self, email: str, password: str):
        try:
            sophomore = self.client_service.get_by_email(email=email)
        except SophomoreEmailException:
            raise NotAuthorizedException
        if not self.authentication_service.verify_password(plain_password=password, hashed_password=sophomore.password):
            raise NotAuthorizedException

        return self.authentication_service.create_jwt(sophomore=sophomore)



