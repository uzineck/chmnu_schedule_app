import punq

from core.apps.schedule.services.room import (
    BaseRoomService,
    ORMRoomService,
)
from core.apps.schedule.use_cases.room.create import CreateRoomUseCase
from core.apps.schedule.use_cases.room.delete import DeleteRoomUseCase
from core.apps.schedule.use_cases.room.get_all import GetAllRoomsUseCase
from core.apps.schedule.use_cases.room.get_list import GetRoomListUseCase
from core.apps.schedule.use_cases.room.update_description import UpdateRoomDescriptionUseCase
from core.apps.schedule.use_cases.room.update_number import UpdateRoomNumberUseCase


def register_room_services(container: punq.Container):
    container.register(BaseRoomService, ORMRoomService)

    container.register(CreateRoomUseCase)
    container.register(GetRoomListUseCase)
    container.register(GetAllRoomsUseCase)
    container.register(UpdateRoomNumberUseCase)
    container.register(UpdateRoomDescriptionUseCase)
    container.register(DeleteRoomUseCase)
