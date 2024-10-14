from dataclasses import dataclass
from typing import Iterable

from core.api.filters import PaginationIn
from core.apps.common.filters import SearchFilter
from core.apps.schedule.entities.room import Room as RoomEntity
from core.apps.schedule.services.room import BaseRoomService


@dataclass
class GetRoomListUseCase:
    room_service: BaseRoomService

    def execute(self, filters: SearchFilter, pagination: PaginationIn) -> tuple[Iterable[RoomEntity], int]:
        room_list = self.room_service.get_room_list(filters=filters, pagination=pagination)
        room_count = self.room_service.get_room_count(filters=filters)

        return room_list, room_count
