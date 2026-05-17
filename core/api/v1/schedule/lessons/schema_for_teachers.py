from ninja import Schema

from core.api.v1.schedule.groups.schemas import GroupSchemaForLesson
from core.api.v1.schedule.rooms.schemas import RoomSchema
from core.api.v1.schedule.subjects.schemas import SubjectSchema
from core.api.v1.schedule.teachers.schemas import TeacherSchema
from core.api.v1.schedule.timeslots.schemas import TimeslotSchema
from core.apps.common.models import LessonType
from core.apps.schedule.entities.teacher import Teacher as TeacherEntity
from core.apps.schedule.entities.views import LessonWithGroupsView


class LessonWithGroupsOutSchema(Schema):
    uuid: str
    type: LessonType
    groups: list[GroupSchemaForLesson]
    subject: SubjectSchema
    room: RoomSchema
    timeslot: TimeslotSchema

    @classmethod
    def from_view(cls, view: LessonWithGroupsView) -> 'LessonWithGroupsOutSchema':
        return cls(
            uuid=view.lesson.uuid,
            type=view.lesson.type,
            subject=SubjectSchema.from_entity(view.lesson.subject),
            room=RoomSchema.from_entity(view.lesson.room),
            timeslot=TimeslotSchema.from_entity(view.lesson.timeslot),
            groups=[GroupSchemaForLesson.from_view(gv) for gv in view.groups],
        )


class TeacherLessonsOutSchema(Schema):
    teacher: TeacherSchema
    lessons: list[LessonWithGroupsOutSchema] | None = None

    @classmethod
    def from_views(
            cls,
            teacher: TeacherEntity,
            views: list[LessonWithGroupsView],
    ) -> 'TeacherLessonsOutSchema':
        return cls(
            teacher=TeacherSchema.from_entity(entity=teacher),
            lessons=[LessonWithGroupsOutSchema.from_view(v) for v in views] if views else None,
        )
