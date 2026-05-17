from ninja import Schema

from core.api.v1.schedule.rooms.schemas import RoomSchema
from core.api.v1.schedule.subjects.schemas import SubjectSchema
from core.api.v1.schedule.teachers.schemas import TeacherSchema
from core.api.v1.schedule.timeslots.schemas import TimeslotSchema
from core.apps.common.models import (
    LessonType,
    Subgroup,
)
from core.apps.schedule.entities.lesson import Lesson as LessonEntity
from core.apps.schedule.entities.views import LessonForGroupView


class LessonForGroupOutSchema(Schema):
    uuid: str
    type: LessonType
    subject: SubjectSchema
    teacher: TeacherSchema
    room: RoomSchema
    timeslot: TimeslotSchema
    subgroups: list[Subgroup] | None = None

    @classmethod
    def from_entity(cls, lesson: LessonEntity) -> 'LessonForGroupOutSchema':
        return cls(
            uuid=lesson.uuid,
            type=lesson.type,
            subject=SubjectSchema.from_entity(lesson.subject),
            teacher=TeacherSchema.from_entity(lesson.teacher),
            room=RoomSchema.from_entity(lesson.room),
            timeslot=TimeslotSchema.from_entity(lesson.timeslot),
        )

    @classmethod
    def from_view(cls, view: LessonForGroupView) -> 'LessonForGroupOutSchema':
        return cls(
            uuid=view.lesson.uuid,
            type=view.lesson.type,
            subject=SubjectSchema.from_entity(view.lesson.subject),
            teacher=TeacherSchema.from_entity(view.lesson.teacher),
            room=RoomSchema.from_entity(view.lesson.room),
            timeslot=TimeslotSchema.from_entity(view.lesson.timeslot),
            subgroups=view.subgroups or None,
        )


class UpdatedLessonOutSchema(Schema):
    updated_lesson: LessonForGroupOutSchema
    old_lesson: LessonForGroupOutSchema

    @classmethod
    def from_entity(cls, updated_lesson: LessonEntity, old_lesson: LessonEntity) -> 'UpdatedLessonOutSchema':
        return cls(
            updated_lesson=LessonForGroupOutSchema.from_entity(lesson=updated_lesson),
            old_lesson=LessonForGroupOutSchema.from_entity(lesson=old_lesson),
        )
