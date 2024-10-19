from dataclasses import dataclass

from core.apps.schedule.entities.room import Room as RoomEntity
from core.apps.schedule.exceptions.room import RoomAlreadyExistException
from core.apps.schedule.services.room import BaseRoomService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class UpdateRoomNumberUseCase:
    room_service: BaseRoomService

    uuid_validator_service: BaseUuidValidatorService

    def execute(self, room_uuid: str, new_number: str) -> RoomEntity:
        self.uuid_validator_service.validate(uuid_str=room_uuid)

        if self.room_service.check_room_number_exists(room_number=new_number):
            raise RoomAlreadyExistException(number=new_number)

        room = self.room_service.get_by_uuid(room_uuid=room_uuid)
        self.room_service.update_number(room_id=room.id, number=new_number)
        updated_room = self.room_service.get_by_id(room_id=room.id)

        return updated_room
