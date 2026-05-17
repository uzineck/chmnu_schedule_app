from collections.abc import Iterable
from dataclasses import dataclass

from core.api.filters import PaginationIn
from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.cache.timeouts import Timeout
from core.apps.common.filters import SearchFilter
from core.apps.schedule.entities.room import Room as RoomEntity
from core.apps.schedule.services.room import BaseRoomService


@dataclass
class GetRoomListUseCase:
    room_service: BaseRoomService

    @cache_decorator.get_or_set_cache(model_prefix='room', func_prefix='list', timeout=Timeout.WEEK)
    def execute(self, filters: SearchFilter, pagination_in: PaginationIn) -> tuple[Iterable[RoomEntity], int]:
        room_list = self.room_service.get_list(filters=filters, pagination=pagination_in)
        room_count = self.room_service.get_count(filters=filters)

        return room_list, room_count
