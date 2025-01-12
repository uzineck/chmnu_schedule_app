from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class ClientNotFoundException(ServiceException):
    email: str | None = None
    id: int | None = None

    @property
    def message(self):
        return 'Клієнта з вказаним ідентифікатором не знайдено'


@dataclass(eq=False)
class ClientAlreadyExistsException(ServiceException):
    email: str

    @property
    def message(self):
        return 'Клієнт з вказаним email вже зареєстрований'


@dataclass(eq=False)
class ClientRoleNotMatchingWithRequiredException(ServiceException):
    client_roles: list[str]
    required_role: str

    @property
    def message(self):
        return 'Клієнт з наданою роллю не відповідає ролі, необхідній для цієї операції'


@dataclass(eq=False)
class ClientUpdateException(ServiceException):
    id: int
    email: str | None = None
    password: str | None = None

    @property
    def message(self):
        return 'Виникла помилка під час оновлення клієнта'
