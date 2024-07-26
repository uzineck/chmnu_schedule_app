from django.db.models import Q

from abc import (
    ABC,
    abstractmethod,
)
from typing import Iterable

from core.apps.schedule.entities.lesson import Lesson as LessonEntity
from core.apps.schedule.exceptions.lesson import LessonNotFoundException
from core.apps.schedule.models import Lesson as LessonModel


class BaseLessonService(ABC):
    @abstractmethod
    def get_lessons_by_id(self, lesson_id: int) -> LessonEntity:
        ...

    @abstractmethod
    def save_lesson(self, lesson: LessonEntity) -> LessonEntity:
        ...

    @abstractmethod
    def get_lessons_for_group(self, group_number: str, group_query: Q) -> Iterable[LessonEntity]:
        ...


class ORMLessonService(BaseLessonService):
    def get_lessons_by_id(self, lesson_id: int) -> LessonEntity:
        try:
            lesson = LessonModel.objects.get(id=lesson_id)
        except LessonModel.DoesNotExist:
            raise LessonNotFoundException(lesson_id=lesson_id)

        return lesson.to_entity()

    def save_lesson(self, lesson: LessonEntity) -> LessonEntity:
        lesson_model = LessonModel.from_entity(lesson=lesson)
        lesson_model.save()

        return lesson_model.to_entity()

    def get_lessons_for_group(self, group_number: str, group_query: Q) -> Iterable[LessonEntity]:
        query = LessonModel.objects.filter(Q(group_lessons__number=group_number) & group_query)

        return [lesson.to_entity() for lesson in query]

