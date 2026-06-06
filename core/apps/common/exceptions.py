import logging
import re
from dataclasses import dataclass
from typing import ClassVar


def _camel_to_snake(name: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).upper()


@dataclass(eq=False)
class ServiceException(Exception):
    """Base for all domain/service exceptions.

    Subclasses configure HTTP status and log severity via class attributes; the
    code defaults to the class name converted to SCREAMING_SNAKE (with any
    `Exception` / `Error` suffix stripped). Override `code` only when the
    auto-derived value is wrong.

    """

    http_status: ClassVar[int] = 500
    log_level: ClassVar[int] = logging.ERROR
    code: ClassVar[str | None] = None

    @classmethod
    def get_code(cls) -> str:
        if cls.code is not None:
            return cls.code
        name = cls.__name__
        for suffix in ("Exception", "Error"):
            if name.endswith(suffix):
                name = name[: -len(suffix)]
                break
        return _camel_to_snake(name)

    @property
    def message(self):
        return 'Application exception occurred'


@dataclass(eq=False)
class NotFoundException(ServiceException):
    http_status: ClassVar[int] = 404
    log_level: ClassVar[int] = logging.INFO


@dataclass(eq=False)
class AlreadyExistsException(ServiceException):
    http_status: ClassVar[int] = 409
    log_level: ClassVar[int] = logging.INFO


@dataclass(eq=False)
class InUseException(ServiceException):
    """Resource is referenced by other resources and cannot be
    modified/deleted."""
    http_status: ClassVar[int] = 409
    log_level: ClassVar[int] = logging.INFO


@dataclass(eq=False)
class UpdateConflictException(ServiceException):
    """Write conflict — row vanished or was modified between read and write."""
    http_status: ClassVar[int] = 409
    log_level: ClassVar[int] = logging.INFO


@dataclass(eq=False)
class ValidationException(ServiceException):
    http_status: ClassVar[int] = 400
    log_level: ClassVar[int] = logging.INFO


@dataclass(eq=False)
class AuthFailureException(ServiceException):
    http_status: ClassVar[int] = 401
    log_level: ClassVar[int] = logging.INFO


@dataclass(eq=False)
class PermissionException(ServiceException):
    http_status: ClassVar[int] = 403
    log_level: ClassVar[int] = logging.INFO


@dataclass(eq=False)
class JWTKeyParsingException(AuthFailureException):
    log_level: ClassVar[int] = logging.WARNING

    @property
    def message(self):
        return 'Invalid JWT Key Error'


@dataclass(eq=False)
class InvalidTokenTypeException(AuthFailureException):
    log_level: ClassVar[int] = logging.WARNING

    @property
    def message(self):
        return 'Invalid token type'
