from ninja import Schema

from core.apps.common.time.entity import TimeInfo as TimeInfoEntity


class TimeInfoOutSchema(Schema):
    current_week_is_even: bool
    current_day: int
    current_lesson: int

    @classmethod
    def from_entity(cls, entity: TimeInfoEntity) -> 'TimeInfoOutSchema':
        return cls(
            current_week_is_even=entity.current_week_is_even,
            current_day=entity.current_day,
            current_lesson=entity.current_lesson,
        )
