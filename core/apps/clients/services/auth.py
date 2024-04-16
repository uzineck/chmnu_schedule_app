from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.apps.common.authentication import BaseAuthenticationService
from core.apps.clients.services.sophomore import BaseSophomoreService


@dataclass(eq=False)
class BaseAuthService(ABC):
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
        sophomore = self.client_service.validate_user(email=email, password=password)
        return self.client_service.generate_token(sophomore=sophomore)



