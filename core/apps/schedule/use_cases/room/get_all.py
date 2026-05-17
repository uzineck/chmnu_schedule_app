from dataclasses import dataclass

from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.cache.timeouts import Timeout
from core.apps.schedule.entities.room import Room as RoomEntity
from core.apps.schedule.services.room import BaseRoomService


@dataclass
class GetAllRoomsUseCase:
    room_service: BaseRoomService

    @cache_decorator.get_or_set_cache(model_prefix='room', func_prefix='all', timeout=Timeout.WEEK)
    def execute(self) -> list[RoomEntity]:
        return list(self.room_service.get_all())
