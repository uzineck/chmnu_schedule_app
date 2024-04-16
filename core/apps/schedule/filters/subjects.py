from dataclasses import dataclass


@dataclass(frozen=True)
class SubjectFilters:
    search: str | None = None
