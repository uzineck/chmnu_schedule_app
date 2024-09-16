from abc import (
    ABC,
    abstractmethod,
)
from collections.abc import Iterable

from core.apps.schedule.entities.group_lessons import GroupLesson as GroupLessonEntity
from core.apps.schedule.models.group import GroupLesson as GroupLessonModel


class BaseGroupLessonService(ABC):
    @abstractmethod
    def save_group_subgroup_lesson(self, group_lesson: GroupLessonEntity) -> GroupLessonEntity:
        ...

    @abstractmethod
    def check_group_subgroup_lesson_exists(self, group_lesson: GroupLessonEntity) -> bool | GroupLessonEntity:
        ...

    @abstractmethod
    def delete_group_subgroup_lesson(self, group_lesson: GroupLessonEntity) -> None:
        ...

    @abstractmethod
    def get_subgroup_from_group_lesson(self, group_id: int, lesson_id: int) -> Iterable[GroupLessonEntity]:
        ...


class ORMGroupLessonService(BaseGroupLessonService):
    def save_group_subgroup_lesson(self, group_lesson: GroupLessonEntity) -> GroupLessonEntity:
        group_lesson_dto = GroupLessonModel.from_entity(entity=group_lesson)
        group_lesson_dto.save()

        return group_lesson_dto.to_entity()

    def check_group_subgroup_lesson_exists(self, group_lesson: GroupLessonEntity) -> bool | GroupLessonEntity:
        existing_group_subgroup_lesson = GroupLessonModel.objects.filter(
            group_id=group_lesson.group.id,
            lesson_id=group_lesson.lesson.id,
            subgroup=group_lesson.subgroup,
        ).first()
        if existing_group_subgroup_lesson:
            return existing_group_subgroup_lesson.to_entity()

        return False

    def delete_group_subgroup_lesson(self, group_lesson: GroupLessonEntity) -> None:
        GroupLessonModel.objects.filter(
            group_id=group_lesson.group.id,
            lesson_id=group_lesson.lesson.id,
            subgroup=group_lesson.subgroup,
        ).delete()

    def get_subgroup_from_group_lesson(self, group_id: int, lesson_id: int) -> Iterable[GroupLessonEntity]:
        group_subgroup_lesson_dto = GroupLessonModel.objects.filter(group_id=group_id, lesson_id=lesson_id)
        return [gsl.to_entity() for gsl in group_subgroup_lesson_dto]
