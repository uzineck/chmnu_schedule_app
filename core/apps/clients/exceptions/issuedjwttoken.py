from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class TokenJTIAlreadyExistsException(ServiceException):
    jti: str | list[str]

    @property
    def message(self):
        return 'Token with provided JTI already exists.'


@dataclass(eq=False)
class ClientTokensRevokedException(ServiceException):
    client_email: str

    @property
    def message(self):
        return 'All client tokens have been revoked. Client needs to login again'
