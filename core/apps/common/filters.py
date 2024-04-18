from dataclasses import dataclass


@dataclass(frozen=True)
class SearchFilter:
    search: str | None = None
