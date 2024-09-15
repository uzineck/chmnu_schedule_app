import punq

from core.apps.schedule.services.teacher import (
    BaseTeacherService,
    ORMTeacherService,
)
from core.apps.schedule.use_cases.teacher.get_lessons_for_teacher import GetLessonsForTeacherUseCase


def register_teacher_services(container: punq.Container):
    container.register(BaseTeacherService, ORMTeacherService)

    container.register(GetLessonsForTeacherUseCase)
