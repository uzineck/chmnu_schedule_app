import punq

from core.apps.schedule.services.group_lessons import (
    BaseGroupLessonService,
    ORMGroupLessonService,
)


def register_group_lesson_services(container: punq.Container):
    container.register(BaseGroupLessonService, ORMGroupLessonService)
