from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Timeslot:
    day: str
    ord_number: int
    is_even: bool
    created_at: datetime
    updated_at: datetime

