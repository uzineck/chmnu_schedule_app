import logging
from abc import (
    ABC,
    abstractmethod,
)

from core.apps.common.models import Subgroup
from core.apps.schedule.entities.group_lessons import GroupLesson as GroupLessonEntity
from core.apps.schedule.exceptions.group_lesson import GroupLessonDeleteError
from core.apps.schedule.models.group import GroupLesson as GroupLessonModel


logger = logging.getLogger(__name__)


class BaseGroupLessonService(ABC):
    @abstractmethod
    def save(self, group_lesson: GroupLessonEntity) -> None:
        ...

    @abstractmethod
    def check_exists(self, group_lesson: GroupLessonEntity) -> bool:
        ...

    @abstractmethod
    def delete(self, group_lesson: GroupLessonEntity) -> None:
        ...

    @abstractmethod
    def get_subgroup_from_group_lesson(self, group_id: int, lesson_id: int) -> list[Subgroup]:
        ...


class ORMGroupLessonService(BaseGroupLessonService):
    def save(self, group_lesson: GroupLessonEntity) -> None:
        group_lesson_dto = GroupLessonModel.from_entity(entity=group_lesson)
        group_lesson_dto.save()

    def check_exists(self, group_lesson: GroupLessonEntity) -> bool:
        return GroupLessonModel.objects.filter(
            group_id=group_lesson.group.id,
            lesson_id=group_lesson.lesson.id,
            subgroup=group_lesson.subgroup,
        ).exists()

    def delete(self, group_lesson: GroupLessonEntity) -> None:
        is_deleted = GroupLessonModel.objects.filter(
            group_id=group_lesson.group.id,
            lesson_id=group_lesson.lesson.id,
            subgroup=group_lesson.subgroup,
        ).delete()

        if not is_deleted:
            logger.error(
                f"Group Lesson Subgroup Relation Delete Error"
                f" ({group_lesson.lesson.id=}, {group_lesson.group.number=}, {group_lesson.subgroup=})",
            )
            raise GroupLessonDeleteError(
                group_number=group_lesson.group.number,
                lesson_uuid=group_lesson.lesson.uuid,
                subgroup=group_lesson.subgroup,
            )

    def get_subgroup_from_group_lesson(self, group_id: int, lesson_id: int) -> list[Subgroup]:
        subgroups = GroupLessonModel.objects.filter(
            group_id=group_id,
            lesson_id=lesson_id,
        ).values_list('subgroup', flat=True)
        return list(subgroups)
