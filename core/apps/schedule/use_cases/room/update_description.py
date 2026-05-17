from dataclasses import dataclass

from core.apps.common.cache.decorator import cache_decorator
from core.apps.schedule.entities.room import Room as RoomEntity
from core.apps.schedule.services.room import BaseRoomService
from core.apps.schedule.validators.room import BaseRoomValidatorService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class UpdateRoomDescriptionUseCase:
    room_service: BaseRoomService

    uuid_validator_service: BaseUuidValidatorService
    room_validator_service: BaseRoomValidatorService

    @cache_decorator.delete_caches([
        dict(model_prefix='room', func_prefix='all'),
        dict(model_prefix='room', func_prefix='list', filters='*', pagination_in='*'),
        dict(model_prefix='group', identifier='*', func_prefix='lessons', filters='*'),
        dict(model_prefix='teacher', identifier='*', func_prefix='lessons', filters='*'),
    ])
    def execute(self, room_uuid: str, description: str) -> RoomEntity:
        self.uuid_validator_service.validate(uuid_str=room_uuid)

        room = self.room_service.get_by_uuid(room_uuid=room_uuid)
        self.room_validator_service.validate(description=description, old_description=room.description)

        self.room_service.update_description(room_id=room.id, description=description)
        updated_room = self.room_service.get_by_id(room_id=room.id)

        return updated_room
