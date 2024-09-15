import punq

from core.apps.schedule.services.timeslot import (
    BaseTimeslotService,
    ORMTimeslotService,
)


def register_timeslot_services(container: punq.Container):
    container.register(BaseTimeslotService, ORMTimeslotService)
