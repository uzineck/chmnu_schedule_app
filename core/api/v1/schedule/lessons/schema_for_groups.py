from ninja import Schema

from datetime import datetime

from core.api.v1.schedule.rooms.schemas import RoomSchema
from core.api.v1.schedule.subjects.schemas import SubjectSchema
from core.api.v1.schedule.teachers.schemas import TeacherSchema
from core.api.v1.schedule.timeslots.schemas import TimeslotSchema
from core.apps.common.models import LessonType
from core.apps.schedule.entities.lesson import Lesson as LessonEntity


class LessonInSchema(Schema):
    type: LessonType

    def to_entity(self):
        return LessonEntity(type=self.type)

    class Config:
        models = LessonType


class CreateLessonInSchema(Schema):
    subject_uuid: str
    teacher_uuid: str
    room_uuid: str
    timeslot_id: int


class LessonForGroupOutSchema(Schema):
    uuid: str
    type: LessonType
    subject: SubjectSchema
    teacher: TeacherSchema
    room: RoomSchema
    timeslot: TimeslotSchema
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, lesson: LessonEntity) -> 'LessonForGroupOutSchema':
        return cls(
            uuid=lesson.uuid,
            type=lesson.type,
            subject=lesson.subject,
            teacher=lesson.teacher,
            room=lesson.room,
            timeslot=lesson.timeslot,
            created_at=lesson.created_at,
            updated_at=lesson.updated_at,
        )
