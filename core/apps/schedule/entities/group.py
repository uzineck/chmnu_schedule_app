from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.common.factory import get_new_uuid
from core.apps.common.models import Subgroup


@dataclass
class Group:
    id: int | None = field(default=None, kw_only=True)  # noqa
    uuid: str | None = field(default_factory=get_new_uuid, kw_only=True)
    number: str | None = field(default=None, kw_only=True)
    headman: ClientEntity | None = field(default=None, kw_only=True)
    has_subgroups: bool = field(default=True, kw_only=True)
    subgroup: Subgroup | None = field(default=None, kw_only=True)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = field(default=None)
