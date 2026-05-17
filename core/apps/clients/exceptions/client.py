from dataclasses import dataclass

from core.apps.common.exceptions import (
    AlreadyExistsException,
    NotFoundException,
    PermissionException,
    UpdateConflictException,
)


@dataclass(eq=False)
class ClientNotFoundException(NotFoundException):
    email: str | None = None
    id: int | None = None

    @property
    def message(self):
        return 'Client with given identifier was not found'


@dataclass(eq=False)
class ClientAlreadyExistsException(AlreadyExistsException):
    email: str

    @property
    def message(self):
        return 'Client with given email is already registered'


@dataclass(eq=False)
class ClientRoleNotMatchingWithRequiredException(PermissionException):
    client_roles: list[str]
    required_role: str

    @property
    def message(self):
        return 'Client roles do not include the role required for this operation'


@dataclass(eq=False)
class ClientUpdateException(UpdateConflictException):
    id: int
    email: str | None = None

    @property
    def message(self):
        return 'Failed to update client'
