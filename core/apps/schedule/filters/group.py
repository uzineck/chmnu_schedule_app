from dataclasses import dataclass

from core.apps.common.models import Subgroup


@dataclass(frozen=True)
class GroupLessonFilter:
    subgroup: Subgroup | None = None
    is_even: bool | None = None
