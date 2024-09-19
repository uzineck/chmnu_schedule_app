from dataclasses import (
    dataclass,
    field,
)


@dataclass
class Token:
    access_token: str = field(default=None)
    refresh_token: str = field(default=None)
