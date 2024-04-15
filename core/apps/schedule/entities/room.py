from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Room:
    number: str
    description: str
    created_at: datetime
    updated_at: datetime
