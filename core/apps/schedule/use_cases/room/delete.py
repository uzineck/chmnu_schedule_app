from dataclasses import dataclass

from core.apps.schedule.services.room import BaseRoomService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class DeleteRoomUseCase:
    room_service: BaseRoomService

    uuid_validator_service: BaseUuidValidatorService

    def execute(self, room_uuid: str) -> None:
        self.uuid_validator_service.validate(uuid_str=room_uuid)

        room = self.room_service.get_by_uuid(room_uuid=room_uuid)
        self.room_service.delete(room_id=room.id)

        return None
