import punq

from core.apps.schedule.services.room import (
    BaseRoomService,
    ORMRoomService,
)


def register_room_services(container: punq.Container):
    container.register(BaseRoomService, ORMRoomService)
