from abc import (
    ABC,
    abstractmethod,
)

from core.apps.clients.models.role import Role as RoleModel


class BaseRoleService(ABC):
    @abstractmethod
    def fetch_roles(self, roles: list[str]) -> list[str]:
        ...


class ORMRoleService(BaseRoleService):
    def fetch_roles(self, roles: list[str]) -> list[str]:
        roles = RoleModel.objects.filter(pk__in=roles)

        return list(roles)
