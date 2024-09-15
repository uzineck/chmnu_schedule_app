from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime

from core.apps.common.factory import get_new_uuid


@dataclass
class Room:
    id: int  | None = field(default=None, kw_only=True)  # noqa
    uuid: str | None = field(default_factory=get_new_uuid, kw_only=True)
    number: str | None = field(default=None, kw_only=True)
    description: str | None = field(default=None, kw_only=True)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = field(default=None)
