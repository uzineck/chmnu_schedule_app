from ninja import Schema

from core.api.v1.schedule.rooms.schemas import RoomSchema
from core.api.v1.schedule.subjects.schemas import SubjectSchema
from core.api.v1.schedule.teachers.schemas import TeacherSchema
from core.api.v1.schedule.timeslots.schemas import TimeslotSchema
from core.apps.common.models import LessonType
from core.apps.schedule.entities.lesson import Lesson as LessonEntity


class LessonForGroupOutSchema(Schema):
    uuid: str
    type: LessonType
    subject: SubjectSchema
    teacher: TeacherSchema
    room: RoomSchema
    timeslot: TimeslotSchema

    @classmethod
    def from_entity(cls, lesson: LessonEntity) -> 'LessonForGroupOutSchema':
        return cls(
            uuid=lesson.uuid,
            type=lesson.type,
            subject=lesson.subject,
            teacher=lesson.teacher,
            room=lesson.room,
            timeslot=lesson.timeslot,
        )
