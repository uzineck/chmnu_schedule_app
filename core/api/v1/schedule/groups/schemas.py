from ninja import Schema

from core.api.v1.clients.clients.schemas import SophomoreSchema
from core.api.v1.schedule.lessons.schema import LessonOutSchema


class GroupSchema(Schema):
    number: str
    sophomore: SophomoreSchema
    has_subgroups: bool


class CreateGroupSchema(Schema):
    number: str
    sophomore_id: int
    has_subgroups: bool


class GroupLessonsOutSchema(Schema):
    group_number: str
    lessons: list[LessonOutSchema] | None = None




