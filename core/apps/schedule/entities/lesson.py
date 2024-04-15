from dataclasses import dataclass, field
from datetime import datetime

from core.apps.schedule.entities.teacher import Teacher
from core.apps.schedule.entities.room import Room
from core.apps.schedule.entities.subject import Subject
from core.apps.schedule.entities.timeslot import Timeslot


@dataclass
class Lesson:
    id: int
    subject: Subject
    teacher: Teacher
    type: str
    room: Room
    timeslot: Timeslot
    subgroup: str
    created_at: datetime
    updated_at: datetime
