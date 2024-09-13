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

    def check_lesson_exists(self, lesson: LessonEntity) -> bool:
        ...

    @abstractmethod
    def get_lessons_for_group(self, group_number: str, group_query: Q) -> Iterable[LessonEntity]:
        ...

    @abstractmethod
    def get_lessons_for_teacher(self, teacher_id: int) -> Iterable[LessonEntity]:
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

    def check_lesson_exists(self, lesson: LessonEntity) -> bool | LessonEntity:
        existing_lesson = LessonModel.objects.filter(
            subject_id=lesson.subject.id,
            teacher_id=lesson.teacher.id,
            room_id=lesson.room.id,
            timeslot_id=lesson.timeslot.id,
            type=lesson.type,
            subgroup=lesson.subgroup,
        ).first()
        if existing_lesson:
            return existing_lesson.to_entity()

        return False

    def get_lessons_for_group(self, group_number: str, group_query: Q) -> Iterable[LessonEntity]:
        query = LessonModel.objects.filter(Q(group_lessons__number=group_number) & group_query)

        return [lesson.to_entity() for lesson in query]

    def get_lessons_for_teacher(self, teacher_id: int) -> Iterable[LessonEntity]:
        query = LessonModel.objects.filter(teacher_id=teacher_id)

        return [lesson.to_entity() for lesson in query]
