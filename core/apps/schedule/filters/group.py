from dataclasses import dataclass

from core.apps.common.models import Subgroup


@dataclass(frozen=True)
class GroupLessonFilter:
    subgroup: Subgroup
    is_even: bool
