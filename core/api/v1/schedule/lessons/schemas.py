from ninja import Schema

from core.api.v1.schedule.timeslots.schemas import CreateTimeslotSchema
from core.apps.common.models import LessonType
from core.apps.schedule.entities.lesson import Lesson as LessonEntity


class LessonInSchema(Schema):
    type: LessonType
    timeslot: CreateTimeslotSchema

    def to_entity(self):
        return LessonEntity(type=self.type, timeslot=self.timeslot.to_entity())


class CreateLessonInSchema(Schema):
    subject_uuid: str
    teacher_uuid: str
    room_uuid: str
