import punq

from core.apps.schedule.services.timeslot import (
    BaseTimeslotService,
    ORMTimeslotService,
)
from core.apps.schedule.use_cases.timeslot.get_or_create import CreateTimeslotUseCase


def register_timeslot_services(container: punq.Container):
    container.register(BaseTimeslotService, ORMTimeslotService)

    container.register(CreateTimeslotUseCase)
