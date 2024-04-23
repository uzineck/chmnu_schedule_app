from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable

from core.apps.clients.entities.sophomore import Sophomore
from core.apps.common.constants import EntityStatus
from core.apps.schedule.entities.lesson import Lesson as LessonEntity


@dataclass
class Group:
    number: str
    has_subgroups: bool = field(default=True, kw_only=True)
    sophomore: Sophomore = field(default=None, kw_only=True)
    lessons: Iterable[LessonEntity] | EntityStatus = field(default=EntityStatus.NOT_LOADED, kw_only=True)
    created_at: datetime
    updated_at: datetime
