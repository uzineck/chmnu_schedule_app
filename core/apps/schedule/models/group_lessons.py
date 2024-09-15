from django.db import models

from core.apps.common.models import (
    Subgroup,
    TimedBaseModel,
)
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

    class Meta:
        verbose_name = "Group Lessons"
        verbose_name_plural = "Groups Lessons"

