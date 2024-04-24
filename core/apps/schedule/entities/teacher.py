from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime
from typing import Iterable

from core.apps.common.constants import EntityStatus
from core.apps.schedule.entities.subject import Subject as SubjectEntity


@dataclass
class Teacher:
    id: int | None = field(default=None, kw_only=True)
    first_name: str
    last_name: str
    middle_name: str
    rank: str
    subjects: Iterable[SubjectEntity] | EntityStatus = field(default=EntityStatus.NOT_LOADED, kw_only=True)
    created_at: datetime
    updated_at: datetime

