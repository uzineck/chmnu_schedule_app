from ninja import Schema

from collections.abc import Iterable

from core.api.v1.clients.schemas import ClientSchemaPrivate
from core.api.v1.schedule.faculty.schemas import FacultyCodeNameSchema
from core.api.v1.schedule.lessons.schema_for_groups import LessonForGroupOutSchema
from core.apps.common.models import Subgroup
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.entities.lesson import Lesson as LessonEntity


class GroupSchema(Schema):
    uuid: str
    number: str
    faculty: FacultyCodeNameSchema
    has_subgroups: bool
    subgroup: Subgroup | None = None

    @classmethod
    def from_entity(cls, entity: GroupEntity) -> 'GroupSchema':
        return cls(
            uuid=entity.uuid,
            number=entity.number,
            faculty=entity.faculty,
            has_subgroups=entity.has_subgroups,
        )

    @classmethod
    def from_entity_with_subgroup(cls, entity: GroupEntity, subgroup: Subgroup | None = None) -> 'GroupSchema':
        return cls(
            uuid=entity.uuid,
            number=entity.number,
            faculty=entity.faculty,
            has_subgroups=entity.has_subgroups,
            subgroup=subgroup,
        )


class GroupSchemaWithHeadman(Schema):
    uuid: str
    number: str
    faculty: FacultyCodeNameSchema
    has_subgroups: bool
    headman: ClientSchemaPrivate

    @classmethod
    def from_entity(cls, entity: GroupEntity) -> 'GroupSchemaWithHeadman':
        return cls(
            uuid=entity.uuid,
            number=entity.number,
            faculty=entity.faculty,
            has_subgroups=entity.has_subgroups,
            headman=entity.headman,
        )


class CreateGroupSchema(Schema):
    number: str
    faculty_uuid: str
    headman_email: str
    has_subgroups: bool


class GroupUuidNumberFacultyOutSchema(Schema):
    uuid: str
    number: str
    faculty: FacultyCodeNameSchema

    @classmethod
    def from_entity(cls, entity: GroupEntity) -> 'GroupUuidNumberFacultyOutSchema':
        return cls(
            uuid=entity.uuid,
            number=entity.number,
            faculty=entity.faculty,
        )


class GroupLessonsOutSchema(Schema):
    group: GroupSchema
    lessons: list[LessonForGroupOutSchema] | None = None

    @classmethod
    def from_entity_with_lesson_entities(
            cls,
            group_entity: GroupEntity,
            lesson_entities: Iterable[LessonEntity],
            subgroup: Subgroup | None = None,
    ) -> 'GroupLessonsOutSchema':
        return cls(
            group=GroupSchema.from_entity_with_subgroup(entity=group_entity, subgroup=subgroup),
            lessons=[LessonForGroupOutSchema.from_entity(obj) for obj in lesson_entities] if lesson_entities else None,
        )


class GroupSchemaForTeacherLesson(Schema):
    uuid: str
    number: str
    faculty: FacultyCodeNameSchema
    subgroups: list[Subgroup] | None = None

    @classmethod
    def from_entity(cls, entity: GroupEntity) -> 'GroupSchemaForTeacherLesson':
        return cls(
            uuid=entity.uuid,
            number=entity.number,
            faculty=entity.faculty,
            has_subgroups=entity.has_subgroups,
            subgroups=entity.subgroups,
        )


class HeadmanEmailInSchema(Schema):
    headman_email: str
