from dataclasses import dataclass

from core.apps.common.cache.decorator import cache_decorator
from core.apps.schedule.exceptions.room import RoomIsUsedInLessonsException
from core.apps.schedule.services.lesson import BaseLessonService
from core.apps.schedule.services.room import BaseRoomService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class DeleteRoomUseCase:
    room_service: BaseRoomService
    lesson_service: BaseLessonService

    uuid_validator_service: BaseUuidValidatorService

    @cache_decorator.delete_caches([
        dict(model_prefix='room', func_prefix='all'),
        dict(model_prefix='room', func_prefix='list', filters='*', pagination_in='*'),
    ])
    def execute(self, room_uuid: str) -> None:
        self.uuid_validator_service.validate(uuid_str=room_uuid)

        room = self.room_service.get_by_uuid(room_uuid=room_uuid)
        if self.lesson_service.check_if_room_has_lessons(room_id=room.id):
            raise RoomIsUsedInLessonsException(id=room.id)

        self.room_service.soft_delete(room_id=room.id)

        return None
