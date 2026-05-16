from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime

from core.apps.clients.entities.client import Client as ClientEntity


@dataclass
class ClientEmailConfirmationToken:
    id: int | None = field(default=None, kw_only=True)  # noqa
    token: str | None = field(default=None, kw_only=True)
    client: ClientEntity | None = field(default=None, kw_only=True)
    expires_at: datetime | None = field(default=None, kw_only=True)
    used_at: datetime | None = field(default=None, kw_only=True)
    created_at: datetime | None = field(default=None, kw_only=True)
    updated_at: datetime | None = field(default=None, kw_only=True)
