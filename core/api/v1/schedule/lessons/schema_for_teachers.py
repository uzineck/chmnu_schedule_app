from ninja import Schema

from datetime import datetime

from core.api.v1.schedule.groups.schemas import GroupSchema
from core.api.v1.schedule.rooms.schemas import RoomSchema
from core.api.v1.schedule.subjects.schemas import SubjectSchema
from core.api.v1.schedule.teachers.schemas import TeacherSchema
from core.api.v1.schedule.timeslots.schemas import TimeslotSchema
from core.apps.common.models import (
    LessonType,
    Subgroup,
)
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.entities.lesson import Lesson as LessonEntity


class LessonForTeacherOutSchema(Schema):
    id: int
    type: LessonType
    groups: list[GroupSchema]
    subgroup: Subgroup
    subject: SubjectSchema
    room: RoomSchema
    timeslot: TimeslotSchema
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, lesson: LessonEntity, groups: list[GroupEntity]) -> 'LessonForTeacherOutSchema':
        return cls(
            id=lesson.id,
            type=lesson.type,
            groups=groups,
            subgroup=lesson.subgroup,
            room=lesson.room,
            timeslot=lesson.timeslot,
            teacher=lesson.teacher,
            subject=lesson.subject,
            created_at=lesson.created_at,
            updated_at=lesson.updated_at,
        )


class TeacherLessonsOutSchema(Schema):
    teacher: TeacherSchema
    lessons: list[LessonForTeacherOutSchema] | None = None
