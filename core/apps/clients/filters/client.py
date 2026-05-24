from dataclasses import (
    dataclass,
    field,
)

from core.apps.common.models import ClientRole


@dataclass(frozen=True)
class ClientSearchFilter:
    search: str | None = None
    allowed_roles: tuple[ClientRole, ...] | None = field(default=None)
