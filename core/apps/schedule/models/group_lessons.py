from django.db import models

from core.apps.common.models import (
    Subgroup,
    TimedBaseModel,
)
from core.apps.schedule.entities.group_lessons import GroupLesson as GroupLessonEntity
from core.apps.schedule.models.group import Group
from core.apps.schedule.models.lesson import Lesson


class GroupLessons(TimedBaseModel):
    group = models.ForeignKey(
        Group,
        verbose_name="Group that has lesson",
        on_delete=models.CASCADE,
        related_name='group_lessons_group',
    )
    lesson = models.ForeignKey(
        Lesson,
        verbose_name="Lesson for the group",
        on_delete=models.CASCADE,
        related_name='group_lessons_lesson',
    )
    subgroup = models.CharField(
        verbose_name="Subgroup of the group that has lesson",
        max_length=1,
        choices=Subgroup,
        null=True,
    )

    def to_entity(self) -> GroupLessonEntity:
        return GroupLessonEntity(
            group=self.group.to_entity(),
            lesson=self.lesson.to_entity(),
            subgroup=Subgroup(self.subgroup),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, entity: GroupLessonEntity) -> 'GroupLessons':
        return cls(
            group_id=entity.group.id,
            lesson_id=entity.lesson.id,
            subgroup=entity.subgroup,
        )

    class Meta:
        verbose_name = "Group Lessons"
        verbose_name_plural = "Groups Lessons"
