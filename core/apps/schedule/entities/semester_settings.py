from dataclasses import dataclass
from datetime import date


@dataclass
class SemesterSettings:
    start_date: date
    is_above_line: bool
