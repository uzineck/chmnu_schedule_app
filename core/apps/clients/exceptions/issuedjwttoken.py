from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class TokenJTIAlreadyExistsException(ServiceException):
    jti: str | list[str]

    @property
    def message(self):
        return 'Токен з наданим JTI вже існує'


@dataclass(eq=False)
class ClientTokensRevokedException(ServiceException):
    client_email: str

    @property
    def message(self):
        return 'Всі клієнтські токени відкликано. Клієнту необхідно повторно увійти в систему'
