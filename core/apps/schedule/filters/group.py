from dataclasses import dataclass

from core.apps.common.models import Subgroup


@dataclass(frozen=True)
class LessonFilter:
    is_even: bool
    subgroup: Subgroup | None = None
