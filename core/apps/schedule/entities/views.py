from dataclasses import (
    dataclass,
    field,
)

from core.apps.common.models import Subgroup
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.entities.lesson import Lesson as LessonEntity


@dataclass(kw_only=True)
class GroupForLessonView:
    group: GroupEntity
    subgroups: list[Subgroup] = field(default_factory=list)


@dataclass(kw_only=True)
class LessonWithGroupsView:
    lesson: LessonEntity
    groups: list[GroupForLessonView] = field(default_factory=list)


@dataclass(kw_only=True)
class LessonForGroupView:
    lesson: LessonEntity
    subgroups: list[Subgroup] = field(default_factory=list)
