from abc import (
    ABC,
    abstractmethod,
)

from core.apps.common.models import Subgroup
from core.apps.schedule.entities.group_lessons import GroupLesson as GroupLessonEntity
from core.apps.schedule.models.group import GroupLesson as GroupLessonModel


class BaseGroupLessonService(ABC):
    @abstractmethod
    def save_group_subgroup_lesson(self, group_lesson: GroupLessonEntity) -> None:
        ...

    @abstractmethod
    def check_group_subgroup_lesson_exists(self, group_lesson: GroupLessonEntity) -> bool:
        ...

    @abstractmethod
    def delete_group_subgroup_lesson(self, group_lesson: GroupLessonEntity) -> None:
        ...

    @abstractmethod
    def get_subgroup_from_group_lesson(self, group_id: int, lesson_id: int) -> list[Subgroup]:
        ...


class ORMGroupLessonService(BaseGroupLessonService):
    def save_group_subgroup_lesson(self, group_lesson: GroupLessonEntity) -> None:
        group_lesson_dto = GroupLessonModel.from_entity(entity=group_lesson)
        group_lesson_dto.save()

    def check_group_subgroup_lesson_exists(self, group_lesson: GroupLessonEntity) -> bool:
        return GroupLessonModel.objects.filter(
            group_id=group_lesson.group.id,
            lesson_id=group_lesson.lesson.id,
            subgroup=group_lesson.subgroup,
        ).exists()

    def delete_group_subgroup_lesson(self, group_lesson: GroupLessonEntity) -> None:
        GroupLessonModel.objects.filter(
            group_id=group_lesson.group.id,
            lesson_id=group_lesson.lesson.id,
            subgroup=group_lesson.subgroup,
        ).delete()

    def get_subgroup_from_group_lesson(self, group_id: int, lesson_id: int) -> list[Subgroup]:
        subgroups = GroupLessonModel.objects.filter(
            group_id=group_id,
            lesson_id=lesson_id,
        ).values_list('subgroup', flat=True)
        return list(subgroups)
