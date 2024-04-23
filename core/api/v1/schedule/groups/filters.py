from ninja import Schema

from core.apps.common.models import Subgroup


class GroupFilter(Schema):
    subgroup: Subgroup | None = None
    is_even: bool | None = None

    class Config:
        model = Subgroup

