import punq

from core.apps.schedule.services.faculty import (
    BaseFacultyService,
    ORMFacultyService,
)
from core.apps.schedule.use_cases.faculty.create import CreateFacultyUseCase
from core.apps.schedule.use_cases.faculty.get_faculty_list import GetFacultyListUseCase


def register_faculty_services(container: punq.Container):
    container.register(BaseFacultyService, ORMFacultyService)

    container.register(CreateFacultyUseCase)
    container.register(GetFacultyListUseCase)
