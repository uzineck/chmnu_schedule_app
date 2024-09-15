from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime

from core.apps.common.models import ClientRole


@dataclass
class Client:
    id: int | None = field(default=None, kw_only=True)
    first_name: str | None = field(default=None, kw_only=True)
    last_name: str | None = field(default=None, kw_only=True)
    middle_name: str | None = field(default=None, kw_only=True)
    role: ClientRole | None = field(default=None, kw_only=True)
    email: str | None = field(default=None, kw_only=True)
    password: str | None = field(default=None, kw_only=True)
    created_at: datetime | None = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = field(default=None, kw_only=True)
