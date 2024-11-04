from dataclasses import (
    dataclass,
    field,
)


@dataclass
class TimeInfo:
    current_week_is_even: bool = field(default=True, kw_only=True)
    current_day: int = field(default=1, kw_only=True)
    current_lesson: int = field(default=-1, kw_only=True)
