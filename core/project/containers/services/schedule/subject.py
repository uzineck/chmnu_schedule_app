import punq

from core.apps.schedule.services.subject import (
    BaseSubjectService,
    ORMSubjectService,
)
from core.apps.schedule.use_cases.subject.create import CreateSubjectUseCase
from core.apps.schedule.use_cases.subject.get_all import GetAllSubjectsUseCase
from core.apps.schedule.use_cases.subject.get_list import GetSubjectListUseCase
from core.apps.schedule.use_cases.subject.update import UpdateSubjectUseCase


def register_subject_services(container: punq.Container):
    container.register(BaseSubjectService, ORMSubjectService)

    container.register(CreateSubjectUseCase)
    container.register(GetAllSubjectsUseCase)
    container.register(GetSubjectListUseCase)
    container.register(UpdateSubjectUseCase)
