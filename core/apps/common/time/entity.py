from dataclasses import dataclass


@dataclass
class TimeInfo:
    current_week_is_even: bool
    current_day: int
    current_lesson: int
