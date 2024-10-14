import punq

from core.apps.schedule.services.teacher import (
    BaseTeacherService,
    ORMTeacherService,
)
from core.apps.schedule.use_cases.teacher.create import CreateTeacherUseCase
from core.apps.schedule.use_cases.teacher.deactivate import DeactivateTeacherUseCase
from core.apps.schedule.use_cases.teacher.get_all import GetAllTeachersUseCase
from core.apps.schedule.use_cases.teacher.get_list import GetTeacherListUseCase
from core.apps.schedule.use_cases.teacher.get_teacher_lessons import GetLessonsForTeacherUseCase
from core.apps.schedule.use_cases.teacher.update_name import UpdateTeacherNameUseCase
from core.apps.schedule.use_cases.teacher.update_rank import UpdateTeacherRankUseCase


def register_teacher_services(container: punq.Container):
    container.register(BaseTeacherService, ORMTeacherService)

    container.register(CreateTeacherUseCase)
    container.register(GetAllTeachersUseCase)
    container.register(GetTeacherListUseCase)
    container.register(GetLessonsForTeacherUseCase)
    container.register(UpdateTeacherNameUseCase)
    container.register(UpdateTeacherRankUseCase)
    container.register(DeactivateTeacherUseCase)
