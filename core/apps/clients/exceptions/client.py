from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class ClientNotFoundException(ServiceException):
    email: str | None = None
    id: int | None = None

    @property
    def message(self):
        return 'Client with provided identifier not found'


@dataclass(eq=False)
class ClientAlreadyExistsException(ServiceException):
    email: str

    @property
    def message(self):
        return 'Client with provided email is already registered'


@dataclass(eq=False)
class ClientRoleNotMatchingWithRequiredException(ServiceException):
    client_role: str
    required_role: str

    @property
    def message(self):
        return 'Client with provided role does not match with the required role for this operation'


@dataclass(eq=False)
class ClientUpdateException(ServiceException):
    id: int
    email: str | None = None
    password: str | None = None

    @property
    def message(self):
        return 'An error occurred while updating client'
