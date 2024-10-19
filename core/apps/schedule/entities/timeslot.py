from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime

from core.apps.common.models import (
    Day,
    OrdinaryNumber,
)


@dataclass
class Timeslot:
    id: int | None = field(default=None, kw_only=True) # noqa
    day: Day | None = field(default=None, kw_only=True)
    ord_number: OrdinaryNumber | None = field(default=None, kw_only=True)
    is_even: bool | None = field(default=None, kw_only=True)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = field(default=None)
