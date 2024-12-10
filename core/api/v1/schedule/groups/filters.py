from ninja import Schema

from core.apps.common.models import Subgroup


class GroupLessonFilter(Schema):
    subgroup: Subgroup
    is_even: bool

    class Config:
        model = Subgroup
