from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime

from core.apps.common.constants import EntityStatus
from core.apps.common.models import (
    LessonType,
    Subgroup,
)
from core.apps.schedule.entities.room import Room
from core.apps.schedule.entities.subject import Subject
from core.apps.schedule.entities.teacher import Teacher
from core.apps.schedule.entities.timeslot import Timeslot


@dataclass
class Lesson:
    id: int | None = field(default=None, kw_only=True)  # noqa
    subject: Subject | EntityStatus = field(default=EntityStatus.NOT_LOADED)
    teacher: Teacher | EntityStatus = field(default=EntityStatus.NOT_LOADED)
    type: str | LessonType = field(default=LessonType.PRACTICE)
    room: Room | EntityStatus = field(default=EntityStatus.NOT_LOADED)
    timeslot: Timeslot | EntityStatus = field(default=EntityStatus.NOT_LOADED)
    subgroup: str | Subgroup = field(default=Subgroup.A)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = field(default=None)
