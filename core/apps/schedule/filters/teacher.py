from dataclasses import dataclass


@dataclass(frozen=True)
class TeacherFilter:
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    rank: str | None = None
