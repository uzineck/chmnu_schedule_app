from django.db import models

from core.apps.clients.models.client import Client
from core.apps.common.models import TimedBaseModel
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.models.lessons import Lesson


class Group(TimedBaseModel):
    number = models.CharField(
        verbose_name="Group Number",
        primary_key=True,
        max_length=10,
        unique=True,
    )
    has_subgroups = models.BooleanField(
        verbose_name="Does group has subgroups",
        default=True,
    )
    sophomore = models.ForeignKey(
        Client,
        verbose_name="Sophomore of the group",
        related_name='group_sophomore',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    lessons = models.ManyToManyField(
        Lesson,
        verbose_name="Group lessons",
        related_name='group_lessons',
        blank=True,
    )

    def to_entity(self):
        return GroupEntity(
            number=self.number,
            has_subgroups=self.has_subgroups,
            sophomore=self.sophomore,
            lessons=self.lessons,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Groups"

