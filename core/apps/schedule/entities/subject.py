from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Subject:
    title: str
    slug: str
    created_at: datetime
    updated_at: datetime
