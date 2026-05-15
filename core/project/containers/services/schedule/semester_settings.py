import punq

from core.apps.schedule.services.semester_settings import (
    BaseSemesterSettingsService,
    ORMSemesterSettingsService,
)


def register_semester_settings_services(container: punq.Container):
    container.register(BaseSemesterSettingsService, ORMSemesterSettingsService)
