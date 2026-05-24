from ninja import Schema

from datetime import datetime

from core.api.v1.clients.schemas import ClientSchemaPrivate
from core.api.v1.schedule.faculty.schemas import FacultyCodeNameSchema
from core.api.v1.schedule.lessons.schema_for_groups import LessonForGroupOutSchema
from core.apps.common.models import Subgroup
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.entities.views import (
    GroupForLessonView,
    LessonForGroupView,
)


class GroupSchema(Schema):
    uuid: str
    number: str
    faculty: FacultyCodeNameSchema
    has_subgroups: bool
    schedule_updated_at: datetime | None = None

    @classmethod
    def from_entity(cls, entity: GroupEntity) -> 'GroupSchema':
        return cls(
            uuid=entity.uuid,
            number=entity.number,
            faculty=FacultyCodeNameSchema.from_entity(entity.faculty),
            has_subgroups=entity.has_subgroups,
            schedule_updated_at=entity.schedule_updated_at,
        )


class GroupSchemaWithSubgroup(GroupSchema):
    subgroup: Subgroup | None = None

    @classmethod
    def from_entity(cls, entity: GroupEntity, subgroup: Subgroup | None = None) -> 'GroupSchemaWithSubgroup':
        return cls(
            uuid=entity.uuid,
            number=entity.number,
            faculty=FacultyCodeNameSchema.from_entity(entity.faculty),
            has_subgroups=entity.has_subgroups,
            schedule_updated_at=entity.schedule_updated_at,
            subgroup=subgroup,
        )


class GroupSchemaWithHeadman(GroupSchema):
    headman: ClientSchemaPrivate | None = None

    @classmethod
    def from_entity(cls, entity: GroupEntity) -> 'GroupSchemaWithHeadman':
        return cls(
            uuid=entity.uuid,
            number=entity.number,
            faculty=FacultyCodeNameSchema.from_entity(entity.faculty),
            has_subgroups=entity.has_subgroups,
            schedule_updated_at=entity.schedule_updated_at,
            headman=ClientSchemaPrivate.from_entity(entity.headman) if entity.headman else None,
        )


class CreateGroupSchema(Schema):
    number: str
    faculty_uuid: str
    headman_email: str
    has_subgroups: bool


class GroupAllOutSchema(GroupSchema):
    """Alias of `GroupSchema` kept for the `get_all_groups` operation_id; the
    full group dataset is identical to the base schema."""


class GroupLessonsOutSchema(Schema):
    group: GroupSchemaWithSubgroup
    lessons: list[LessonForGroupOutSchema] | None = None

    @classmethod
    def from_views(
            cls,
            group_entity: GroupEntity,
            lesson_views: list[LessonForGroupView],
            subgroup: Subgroup | None = None,
    ) -> 'GroupLessonsOutSchema':
        return cls(
            group=GroupSchemaWithSubgroup.from_entity(entity=group_entity, subgroup=subgroup),
            lessons=[LessonForGroupOutSchema.from_view(v) for v in lesson_views] if lesson_views else None,
        )


class GroupSchemaForLesson(Schema):
    uuid: str
    number: str
    subgroups: list[Subgroup] | None = None

    @classmethod
    def from_view(cls, view: 'GroupForLessonView') -> 'GroupSchemaForLesson':
        return cls(
            uuid=view.group.uuid,
            number=view.group.number,
            subgroups=view.subgroups or None,
        )


class HeadmanEmailInSchema(Schema):
    headman_email: str
