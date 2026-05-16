from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime

from core.apps.common.models import Subgroup
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.entities.lesson import Lesson as LessonEntity


@dataclass
class GroupLesson:
    id: int | None = field(default=None, kw_only=True)  # noqa
    group: GroupEntity | None = field(default=None, kw_only=True)
    subgroup: Subgroup | None = field(default=None, kw_only=True)
    lesson: LessonEntity | None = field(default=None, kw_only=True)
    created_at: datetime | None = field(default=None, kw_only=True)
    updated_at: datetime | None = field(default=None, kw_only=True)
