from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime

from core.apps.common.constants import EntityStatus
from core.apps.common.models import Subgroup
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.entities.lesson import Lesson as LessonEntity


@dataclass
class GroupLesson:
    id: int | None = field(default=None, kw_only=True)  # noqa
    group: GroupEntity | EntityStatus = field(default=EntityStatus.NOT_LOADED)
    subgroup: Subgroup | None = field(default=None, kw_only=True)
    lesson: LessonEntity | EntityStatus = field(default=EntityStatus.NOT_LOADED)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = field(default=None)
