from ninja import Schema

from core.apps.common.time.entity import TimeInfo as TimeInfoEntity


class TimeInfoOutSchema(Schema):
    is_even: bool
    day: int
    lesson: int

    @classmethod
    def from_entity(cls, entity: TimeInfoEntity) -> 'TimeInfoOutSchema':
        return cls(
            is_even=entity.current_week_is_even,
            day=entity.current_day,
            lesson=entity.current_lesson,
        )
