from dataclasses import (
    dataclass,
    field,
)


@dataclass
class Token:
    access_token: str | None = field(default=None)
    refresh_token: str | None = field(default=None)
