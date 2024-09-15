from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime
from typing import Iterable

from core.apps.common.constants import EntityStatus
from core.apps.common.factory import get_new_uuid
from core.apps.schedule.entities.subject import Subject as SubjectEntity


@dataclass
class Teacher:
    id: int | None = field(default=None, kw_only=True) # noqa
    uuid: str | None = field(default_factory=get_new_uuid, kw_only=True)
    first_name: str | None = field(default=None, kw_only=True)
    last_name: str | None = field(default=None, kw_only=True)
    middle_name: str | None = field(default=None, kw_only=True)
    rank: str | None = field(default=None, kw_only=True)
    subjects: Iterable[SubjectEntity] | EntityStatus = field(default=EntityStatus.NOT_LOADED, kw_only=True)
    is_active: bool = field(default=True, kw_only=True)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = field(default=None)
