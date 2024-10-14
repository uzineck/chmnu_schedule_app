from dataclasses import dataclass

from core.apps.schedule.entities.room import Room as RoomEntity
from core.apps.schedule.services.room import BaseRoomService


@dataclass
class CreateRoomUseCase:
    room_service: BaseRoomService

    def execute(self, number: str) -> RoomEntity:
        room = self.room_service.create(number=number)

        return room
