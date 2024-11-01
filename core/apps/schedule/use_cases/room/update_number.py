from dataclasses import dataclass

from core.apps.schedule.entities.room import Room as RoomEntity
from core.apps.schedule.services.room import BaseRoomService
from core.apps.schedule.validators.room import BaseRoomValidatorService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class UpdateRoomNumberUseCase:
    room_service: BaseRoomService

    uuid_validator_service: BaseUuidValidatorService
    room_validator_service: BaseRoomValidatorService

    def execute(self, room_uuid: str, new_number: str) -> RoomEntity:
        self.uuid_validator_service.validate(uuid_str=room_uuid)

        room = self.room_service.get_by_uuid(room_uuid=room_uuid)
        self.room_validator_service.validate(number=new_number, old_number=room.number)

        self.room_service.update_number(room_id=room.id, number=new_number)
        updated_room = self.room_service.get_by_id(room_id=room.id)

        return updated_room
