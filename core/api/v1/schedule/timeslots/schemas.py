from ninja import Schema

from core.apps.common.models import Day, OrdinaryNumber


class CreateTimeslotSchema(Schema):
    day: Day
    ord_number: OrdinaryNumber
    is_even: bool

    class Config:
        model = Day, OrdinaryNumber


class TimeslotSchema(CreateTimeslotSchema):
    id: int


class TimeslotInSchema(Schema):
    timeslot_id: int
