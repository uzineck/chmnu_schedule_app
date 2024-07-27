from ninja import Schema

from core.api.v1.clients.schemas import ClientSchema
from core.api.v1.schedule.lessons.schema_for_groups import LessonForGroupOutSchema
from core.apps.schedule.entities.group import Group as GroupEntity


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


class ListGroupSchema(Schema):
    groups: list[GroupSchema] | None = None


class UpdateGroupHeadmanSchema(Schema):
    group_number: str
    headman_email: str



