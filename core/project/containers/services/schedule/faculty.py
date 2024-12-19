import punq

from core.apps.schedule.services.faculty import (
    BaseFacultyService,
    ORMFacultyService,
)
from core.apps.schedule.use_cases.faculty.create import CreateFacultyUseCase
from core.apps.schedule.use_cases.faculty.delete import DeleteFacultyUseCase
from core.apps.schedule.use_cases.faculty.get_all import GetAllFacultiesUseCase
from core.apps.schedule.use_cases.faculty.get_list import GetFacultyListUseCase
from core.apps.schedule.use_cases.faculty.update_code_name import UpdateFacultyCodeNameUseCase
from core.apps.schedule.use_cases.faculty.update_name import UpdateFacultyNameUseCase


def register_faculty_services(container: punq.Container):
    container.register(BaseFacultyService, ORMFacultyService)

    container.register(CreateFacultyUseCase)
    container.register(GetFacultyListUseCase)
    container.register(GetAllFacultiesUseCase)
    container.register(UpdateFacultyNameUseCase)
    container.register(UpdateFacultyCodeNameUseCase)
    container.register(DeleteFacultyUseCase)
