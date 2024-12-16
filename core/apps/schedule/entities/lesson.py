from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime

from core.apps.common.constants import EntityStatus
from core.apps.common.factory import get_new_uuid
from core.apps.common.models import LessonType
from core.apps.schedule.entities.room import Room as RoomEntity
from core.apps.schedule.entities.subject import Subject as SubjectEntity
from core.apps.schedule.entities.teacher import Teacher as TeacherEntity
from core.apps.schedule.entities.timeslot import Timeslot as TimeslotEntity


@dataclass
class Lesson:
    id: int | None = field(default=None, kw_only=True)  # noqa
    uuid: str | None = field(default_factory=get_new_uuid, kw_only=True)
    type: str | LessonType = field(default=LessonType.PRACTICE)
    subject: SubjectEntity | EntityStatus = field(default=EntityStatus.NOT_LOADED)
    teacher: TeacherEntity | EntityStatus = field(default=EntityStatus.NOT_LOADED)
    room: RoomEntity | EntityStatus = field(default=EntityStatus.NOT_LOADED)
    timeslot: TimeslotEntity | EntityStatus = field(default=EntityStatus.NOT_LOADED)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = field(default=None)
