from ninja import Schema

from core.api.v1.clients.schemas import ClientSchema
from core.api.v1.schedule.lessons.schema import LessonOutSchema


class GroupSchema(Schema):
    number: str
    headman: ClientSchema
    has_subgroups: bool


class CreateGroupSchema(Schema):
    number: str
    headman_email: str
    has_subgroups: bool


class GroupLessonsOutSchema(GroupSchema):
    lessons: list[LessonOutSchema] | None = None


class UpdateGroupHeadmanSchema(Schema):
    group_number: str
    headman_email: str



