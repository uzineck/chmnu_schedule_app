import punq

from core.apps.common.time.service import (
    BaseTimeService,
    DatetimeTimeService,
)
from core.apps.common.time.use_case import GetCurrentTimeInfoUseCase


def register_time_services(container: punq.Container):
    container.register(BaseTimeService, DatetimeTimeService)

    container.register(GetCurrentTimeInfoUseCase)
