from dataclasses import dataclass
from datetime import datetime


@dataclass
class Room:
    id: int
    number: str
    description: str
    created_at: datetime
    updated_at: datetime
