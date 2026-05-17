import logging
from dataclasses import dataclass
from typing import ClassVar

from core.apps.common.exceptions import (
    AlreadyExistsException,
    AuthFailureException,
)


@dataclass(eq=False)
class TokenJTIAlreadyExistsException(AlreadyExistsException):
    log_level: ClassVar[int] = logging.WARNING

    jti: str | list[str]

    @property
    def message(self):
        return 'Token with given JTI already exists'


@dataclass(eq=False)
class ClientTokensRevokedException(AuthFailureException):
    log_level: ClassVar[int] = logging.WARNING

    client_email: str

    @property
    def message(self):
        return 'All client tokens have been revoked. Client must log in again.'
