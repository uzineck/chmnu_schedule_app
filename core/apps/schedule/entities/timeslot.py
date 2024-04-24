from dataclasses import dataclass
from datetime import datetime


@dataclass
class Timeslot:
    id: int
    day: str
    ord_number: int
    is_even: bool
    created_at: datetime
    updated_at: datetime

