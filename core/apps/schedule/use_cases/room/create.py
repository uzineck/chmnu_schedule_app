from dataclasses import dataclass

from core.apps.common.cache.decorator import cache_decorator
from core.apps.schedule.entities.room import Room as RoomEntity
from core.apps.schedule.services.room import BaseRoomService
from core.apps.schedule.validators.room import BaseRoomValidatorService


@dataclass
class CreateRoomUseCase:
    room_service: BaseRoomService

    room_validator_service: BaseRoomValidatorService

    @cache_decorator.delete_caches([
        dict(model_prefix='room', func_prefix='all'),
        dict(model_prefix='room', func_prefix='list', filters='*', pagination_in='*'),
    ])
    def execute(self, number: str) -> RoomEntity:
        self.room_validator_service.validate(number=number)

        existing = self.room_service.find_any_by_number(room_number=number)
        if existing is not None and not existing.is_active:
            self.room_service.restore(room_id=existing.id)
            return self.room_service.get_by_id(room_id=existing.id)

        return self.room_service.create(number=number)
