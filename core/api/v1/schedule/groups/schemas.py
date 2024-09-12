from ninja import Schema

from collections.abc import Iterable

from core.api.v1.clients.schemas import ClientSchema
from core.api.v1.schedule.lessons.schema_for_groups import LessonForGroupOutSchema
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.entities.lesson import Lesson as LessonEntity


class GroupSchema(Schema):
    number: str
    headman: ClientSchema
    has_subgroups: bool

    @classmethod
    def from_entity(cls, entity: GroupEntity) -> 'GroupSchema':
        return cls(
            number=entity.number,
            headman=entity.headman,
            has_subgroups=entity.has_subgroups,
        )


class CreateGroupSchema(Schema):
    number: str
    headman_email: str
    has_subgroups: bool


class GroupLessonsOutSchema(GroupSchema):
    lessons: list[LessonForGroupOutSchema] | None = None

    @classmethod
    def from_entity_with_lesson_entities(
            cls,
            group_entity: GroupEntity,
            lesson_entities: Iterable[LessonEntity],
    ) -> 'GroupLessonsOutSchema':
        return cls(
            number=group_entity.number,
            headman=group_entity.headman,
            has_subgroups=group_entity.has_subgroups,
            lessons=[LessonForGroupOutSchema.from_entity(obj) for obj in lesson_entities] if lesson_entities else None,
        )

    @classmethod
    def from_entity(cls, entity: GroupEntity) -> 'GroupLessonsOutSchema':
        return cls(
            number=entity.number,
            headman=entity.headman,
            has_subgroups=entity.has_subgroups,
            lessons=entity.lessons if entity.lessons else None,
        )


class UpdateGroupHeadmanSchema(Schema):
    group_number: str
    new_headman_email: str



