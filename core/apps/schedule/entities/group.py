from dataclasses import dataclass, field
from datetime import datetime

from core.apps.clients.entities.sophomore import Sophomore
from core.apps.schedule.entities.lesson import Lesson


@dataclass
class Group:
    number: str
    has_subgroups: bool = field(default=True, kw_only=True)
    sophomore: Sophomore = field(default=None, kw_only=True)
    lessons: Lesson = field(default=None, kw_only=True)
    created_at: datetime
    updated_at: datetime
