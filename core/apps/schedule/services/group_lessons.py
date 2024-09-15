from abc import (
    ABC,
    abstractmethod,
)

from core.apps.schedule.entities.group_lessons import GroupLesson as GroupLessonEntity
from core.apps.schedule.models import GroupLessons as GroupLessonModel


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


