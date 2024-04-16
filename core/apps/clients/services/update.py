from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.apps.clients.services.sophomore import BaseSophomoreService


@dataclass(eq=False)
class BaseUpdateUserService(ABC):
    client_service: BaseSophomoreService

    @abstractmethod
    def change_password(self, email: str, old_password: str, new_password: str):
        ...

    @abstractmethod
    def change_email(self, old_email: str, new_email: str, password: str):
        ...


class UpdateUserService(BaseUpdateUserService):
    def change_password(self, email: str, old_password: str, new_password: str):
        sophomore = self.client_service.validate_user(email=email, password=old_password)
        self.client_service.update_password(sophomore=sophomore, plain_password=new_password)

    def change_email(self, old_email: str, new_email: str, password: str):
        sophomore = self.client_service.validate_user(email=old_email, password=password)
        updated_sophomore = self.client_service.update_email(sophomore=sophomore, email=new_email)
        return new_email, self.client_service.generate_token(sophomore=updated_sophomore)

    def change_credentials(self, email: str, first_name: str, last_name: str, middle_name: str):
        sophomore = self.client_service.get_by_email(email=email)
        updated_sophomore = self.client_service.update_credentials(sophomore=sophomore,
                                                                   first_name=first_name,
                                                                   last_name=last_name,
                                                                   middle_name=middle_name)

        return updated_sophomore

