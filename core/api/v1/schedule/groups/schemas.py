from ninja import Schema

from collections.abc import Iterable

from core.api.v1.clients.schemas import ClientSchemaPrivate
from core.api.v1.schedule.lessons.schema_for_groups import LessonForGroupOutSchema
from core.apps.common.models import Subgroup
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.entities.lesson import Lesson as LessonEntity


class GroupSchema(Schema):
    uuid: str
    number: str
    has_subgroups: bool
    subgroup: Subgroup | None = None

    @classmethod
    def from_entity(cls, entity: GroupEntity) -> 'GroupSchema':
        return cls(
            uuid=entity.uuid,
            number=entity.number,
            has_subgroups=entity.has_subgroups,
        )

    @classmethod
    def from_entity_with_subgroup(cls, entity: GroupEntity) -> 'GroupSchema':
        return cls(
            uuid=entity.uuid,
            number=entity.number,
            has_subgroups=entity.has_subgroups,
            subgroup=entity.subgroup,
        )


class GroupSchemaWithHeadman(Schema):
    uuid: str
    number: str
    has_subgroups: bool
    headman: ClientSchemaPrivate

    @classmethod
    def from_entity(cls, entity: GroupEntity) -> 'GroupSchemaWithHeadman':
        return cls(
            uuid=entity.uuid,
            number=entity.number,
            has_subgroups=entity.has_subgroups,
            headman=entity.headman,
        )


class CreateGroupSchema(Schema):
    number: str
    headman_email: str
    has_subgroups: bool


class UpdateGroupHeadmanSchema(Schema):
    group_number: str
    new_headman_email: str


class GroupUuidNumberOutSchema(Schema):
    uuid: str
    number: str

    @classmethod
    def from_entity(cls, entity: GroupEntity) -> 'GroupUuidNumberOutSchema':
        return cls(
            uuid=entity.uuid,
            number=entity.number,
        )


class GroupLessonsOutSchema(GroupSchema):
    lessons: list[LessonForGroupOutSchema] | None = None

    @classmethod
    def from_entity_with_lesson_entities(
            cls,
            group_entity: GroupEntity,
            lesson_entities: Iterable[LessonEntity],
            subgroup: Subgroup | None = None,
    ) -> 'GroupLessonsOutSchema':
        return cls(
            uuid=group_entity.uuid,
            number=group_entity.number,
            has_subgroups=group_entity.has_subgroups,
            subgroup=subgroup,
            lessons=[LessonForGroupOutSchema.from_entity(obj) for obj in lesson_entities] if lesson_entities else None,
        )

    @classmethod
    def from_entity(
            cls,
            entity: GroupEntity,
            subgroup: Subgroup | None = None,
    ) -> 'GroupLessonsOutSchema':
        return cls(
            uuid=entity.uuid,
            number=entity.number,
            has_subgroups=entity.has_subgroups,
            subgroup=subgroup,
            lessons=entity.lessons if entity.lessons else None,
        )
