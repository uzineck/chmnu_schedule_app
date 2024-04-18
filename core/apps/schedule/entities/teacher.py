from dataclasses import dataclass, field
from datetime import datetime

from core.apps.common.constants import EntityStatus
from core.apps.schedule.entities.subject import Subject


@dataclass
class Teacher:
    id: int | None = field(default=None, kw_only=True)
    first_name: str
    last_name: str
    middle_name: str
    rank: str
    subjects: Subject | EntityStatus = field(default=EntityStatus.NOT_LOADED, kw_only=True)
    created_at: datetime
    updated_at: datetime

