from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime

from core.apps.common.models import ClientRole


@dataclass
class Client:
    id: int | None = field(default=None, kw_only=True)  # noqa
    first_name: str | None = field(default=None, kw_only=True)
    last_name: str | None = field(default=None, kw_only=True)
    middle_name: str | None = field(default=None, kw_only=True)
    roles: list[ClientRole] = field(default_factory=list, kw_only=True)
    email: str | None = field(default=None, kw_only=True)
    is_email_confirmed: bool = field(default=False, kw_only=True)
    created_at: datetime | None = field(default=None, kw_only=True)
    updated_at: datetime | None = field(default=None, kw_only=True)
