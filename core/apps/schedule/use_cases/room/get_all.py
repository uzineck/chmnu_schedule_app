from dataclasses import dataclass
from typing import Iterable

from core.apps.schedule.entities.room import Room as RoomEntity
from core.apps.schedule.services.room import BaseRoomService


@dataclass
class GetAllRoomsUseCase:
    room_service: BaseRoomService

    def execute(self) -> Iterable[RoomEntity]:
        rooms = self.room_service.get_all()
        return rooms
