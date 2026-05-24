from dataclasses import dataclass


@dataclass(frozen=True)
class TeacherFilter:
    name: str | None = None
    rank: str | None = None
