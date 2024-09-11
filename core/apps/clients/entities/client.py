from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime

from core.apps.common.models import ClientRole


@dataclass
class Client:
    id: int | None = field(default=None, kw_only=True)
    first_name: str
    last_name: str
    middle_name: str
    role: ClientRole
    email: str
    password: str
    created_at: datetime | None = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = field(default=None, kw_only=True)
