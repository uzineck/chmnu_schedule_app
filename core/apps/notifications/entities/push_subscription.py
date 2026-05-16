from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime

from core.apps.common.factory import get_new_uuid
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.entities.teacher import Teacher as TeacherEntity


@dataclass
class GroupPushSubscription:
    id: int | None = field(default=None, kw_only=True)  # noqa
    external_id: str | None = field(default_factory=get_new_uuid, kw_only=True)
    player_id: str | None = field(default=None, kw_only=True)
    group: GroupEntity | None = field(default=None, kw_only=True)
    is_active: bool = field(default=True, kw_only=True)
    last_seen_at: datetime | None = field(default=None, kw_only=True)
    created_at: datetime | None = field(default=None, kw_only=True)
    updated_at: datetime | None = field(default=None, kw_only=True)


@dataclass
class TeacherPushSubscription:
    id: int | None = field(default=None, kw_only=True)  # noqa
    external_id: str | None = field(default_factory=get_new_uuid, kw_only=True)
    player_id: str | None = field(default=None, kw_only=True)
    teacher: TeacherEntity | None = field(default=None, kw_only=True)
    is_active: bool = field(default=True, kw_only=True)
    last_seen_at: datetime | None = field(default=None, kw_only=True)
    created_at: datetime | None = field(default=None, kw_only=True)
    updated_at: datetime | None = field(default=None, kw_only=True)
