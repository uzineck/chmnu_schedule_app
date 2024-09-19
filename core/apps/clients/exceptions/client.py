from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException


@dataclass(eq=False)
class ClientEmailNotFoundException(ServiceException):
    email: str

    @property
    def message(self):
        return 'Clients\' with provided email not found'


@dataclass(eq=False)
class ClientAlreadyExistsException(ServiceException):
    email: str

    @property
    def message(self):
        return 'Client with provided email is already registered'


@dataclass(eq=False)
class ClientRoleNotMatchingWithRequired(ServiceException):
    client_role: str

    @property
    def message(self):
        return 'Client with provided role does not match with the required role for this operation'
