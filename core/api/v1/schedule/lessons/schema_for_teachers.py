from ninja import Schema

from typing import Iterable

from core.api.v1.schedule.groups.schemas import GroupSchemaForTeacherLesson
from core.api.v1.schedule.rooms.schemas import RoomSchema
from core.api.v1.schedule.subjects.schemas import SubjectSchema
from core.api.v1.schedule.teachers.schemas import TeacherSchema
from core.api.v1.schedule.timeslots.schemas import TimeslotSchema
from core.apps.common.models import LessonType
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.entities.lesson import Lesson as LessonEntity
from core.apps.schedule.entities.teacher import Teacher as TeacherEntity


class LessonForTeacherOutSchema(Schema):
    uuid: str
    type: LessonType
    groups: list[GroupSchemaForTeacherLesson]
    subject: SubjectSchema
    room: RoomSchema
    timeslot: TimeslotSchema

    @classmethod
    def from_entity(cls, lesson: LessonEntity, groups: list[GroupEntity]) -> 'LessonForTeacherOutSchema':
        return cls(
            uuid=lesson.uuid,
            type=lesson.type,
            groups=groups,
            room=RoomSchema.from_entity(lesson.room),
            timeslot=TimeslotSchema.from_entity(lesson.timeslot),
            subject=SubjectSchema.from_entity(lesson.subject),
        )


class TeacherLessonsOutSchema(Schema):
    teacher: TeacherSchema
    lessons: list[LessonForTeacherOutSchema] | None = None

    @classmethod
    def from_entity_with_lesson_entities(
            cls,
            teacher_entity: TeacherEntity,
            lesson_entities: Iterable[LessonEntity],
            group_entities: dict[int, [GroupEntity]],
    ) -> 'TeacherLessonsOutSchema':
        return cls(
            teacher=TeacherSchema.from_entity(entity=teacher_entity),
            lessons=[
                LessonForTeacherOutSchema.from_entity(
                    lesson,
                    group_entities.get(lesson.id, []),
                ) for lesson in lesson_entities
            ] if lesson_entities else None,
        )
