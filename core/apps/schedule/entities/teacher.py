from dataclasses import dataclass, field
from datetime import datetime

from core.apps.schedule.entities.subject import Subject


@dataclass
class Teacher:
    id: int
    first_name: str
    last_name: str
    middle_name: str
    rank: str
    subjects: Subject
    created_at: datetime
    updated_at: datetime

