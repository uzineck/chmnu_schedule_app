from ninja import Schema

from core.apps.common.models import (
    Day,
    OrdinaryNumber,
)
from core.apps.schedule.entities.timeslot import Timeslot as TimeslotEntity


class CreateTimeslotSchema(Schema):
    day: Day
    ord_number: OrdinaryNumber
    is_even: bool

    def to_entity(self) -> TimeslotEntity:
        return TimeslotEntity(
            day=self.day,
            ord_number=self.ord_number,
            is_even=self.is_even,
        )


class TimeslotSchema(CreateTimeslotSchema):
    id: int

    @classmethod
    def from_entity(cls, entity: TimeslotEntity) -> 'TimeslotSchema':
        return cls(
            id=entity.id,
            day=entity.day,
            ord_number=entity.ord_number,
            is_even=entity.is_even,
        )


class TimeslotInSchema(Schema):
    timeslot_id: int
