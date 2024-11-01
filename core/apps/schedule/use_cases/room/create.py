from dataclasses import dataclass

from core.apps.schedule.entities.room import Room as RoomEntity
from core.apps.schedule.services.room import BaseRoomService
from core.apps.schedule.validators.room import BaseRoomValidatorService


@dataclass
class CreateRoomUseCase:
    room_service: BaseRoomService

    room_validator_service: BaseRoomValidatorService

    def execute(self, number: str) -> RoomEntity:
        self.room_validator_service.validate(number=number)

        room = self.room_service.create(number=number)

        return room
