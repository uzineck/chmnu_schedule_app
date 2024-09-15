import punq

from core.apps.schedule.services.subject import (
    BaseSubjectService,
    ORMSubjectService,
)


def register_subject_services(container: punq.Container):
    container.register(BaseSubjectService, ORMSubjectService)
