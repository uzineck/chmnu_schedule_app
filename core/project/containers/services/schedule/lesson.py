import punq

from core.apps.schedule.services.lesson import (
    BaseLessonService,
    ORMLessonService,
)
from core.apps.schedule.use_cases.lesson.create import CreateLessonUseCase
from core.apps.schedule.use_cases.lesson.update import UpdateLessonUseCase


def register_lesson_services(container: punq.Container):
    container.register(BaseLessonService, ORMLessonService)

    container.register(CreateLessonUseCase)
    container.register(UpdateLessonUseCase)
