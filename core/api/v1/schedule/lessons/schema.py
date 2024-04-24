from ninja import Schema

from datetime import datetime

from core.api.v1.schedule.rooms.schemas import RoomSchema
from core.api.v1.schedule.subjects.schemas import SubjectSchema
from core.api.v1.schedule.teachers.schemas import TeacherSchema
from core.api.v1.schedule.timeslots.schemas import TimeslotSchema
from core.apps.common.models import (
    LessonType,
    Subgroup,
)
from core.apps.schedule.entities.lesson import Lesson as LessonEntity


class LessonInSchema(Schema):
    type: LessonType
    subgroup: Subgroup

    def to_entity(self):
        return LessonEntity(type=self.type, subgroup=self.subgroup)

    class Config:
        models = LessonType, Subgroup


class CreateLessonInSchema(Schema):
    subject_id: int
    teacher_id: int
    room_id: int
    timeslot_id: int


class LessonOutSchema(Schema):
    id: int
    subject: SubjectSchema
    teacher: TeacherSchema
    type: LessonType
    subgroup: Subgroup
    room: RoomSchema
    timeslot: TimeslotSchema
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, lesson: LessonEntity) -> 'LessonOutSchema':
        return cls(
            id=lesson.id,
            type=lesson.type,
            subgroup=lesson.subgroup,
            room=lesson.room,
            timeslot=lesson.timeslot,
            teacher=lesson.teacher,
            subject=lesson.subject,
            created_at=lesson.created_at,
            updated_at=lesson.updated_at,
        )

