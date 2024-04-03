from django.db import models

from core.apps.common.models import TimedBaseModel
from core.apps.schedule.models.lessons import Lesson
from core.apps.schedule.models.sophomors import Sophomore


class Group(TimedBaseModel):
    number = models.CharField(
        verbose_name="Group Number",
        primary_key=True,
        max_length=10,
        unique=True
    )
    has_subgroups = models.BooleanField(
        verbose_name="Does group has subgroups",
        default=True,
    )
    sophomore = models.ForeignKey(
        Sophomore,
        verbose_name="Sophomore of the group",
        related_name='group_sophomore',
        on_delete=models.CASCADE,
    )
    lessons = models.ManyToManyField(
        Lesson,
        verbose_name="Group lessons",
        related_name='group_lessons')

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Groups"

