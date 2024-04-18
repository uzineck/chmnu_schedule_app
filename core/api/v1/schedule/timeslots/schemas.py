from ninja import Schema

from core.apps.common.models import Day, OrdinaryNumber


class TimeslotSchema(Schema):
    day: Day
    ord_number: OrdinaryNumber
    is_even: bool

    class Config:
        model = Day, OrdinaryNumber
