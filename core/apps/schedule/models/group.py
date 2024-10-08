from django.db import models

import uuid

from core.apps.clients.models.client import Client
from core.apps.common.models import (
    Subgroup,
    TimedBaseModel,
)
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.entities.group_lessons import GroupLesson as GroupLessonEntity
from core.apps.schedule.models.faculty import Faculty
from core.apps.schedule.models.lesson import Lesson


class Group(TimedBaseModel):
    group_uuid = models.UUIDField(
        verbose_name='UUID group representation',
        editable=False,
        default=uuid.uuid4,
    )
    number = models.CharField(
        verbose_name="Group Number",
        max_length=10,
        unique=True,
    )
    faculty = models.ForeignKey(
        Faculty,
        verbose_name="Faculty the group belongs to",
        on_delete=models.PROTECT,
        related_name='group_faculty',
        blank=True,
        null=True,
    )
    has_subgroups = models.BooleanField(
        verbose_name="Does group has subgroups",
        default=True,
    )
    headman = models.ForeignKey(
        Client,
        verbose_name="Headman of the group",
        related_name='group_headman',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    lessons = models.ManyToManyField(
        Lesson,
        verbose_name="Lessons of the group",
        related_name='group_lessons',
        through='GroupLesson',
        blank=True,
    )

    def to_entity(self) -> GroupEntity:
        return GroupEntity(
            id=self.id,
            uuid=str(self.group_uuid),
            number=self.number,
            faculty=self.faculty.to_entity(),
            has_subgroups=self.has_subgroups,
            headman=self.headman.to_entity(),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Groups"
        indexes = [
            models.Index(fields=['group_uuid']),
            models.Index(fields=['number']),
        ]


class GroupLesson(TimedBaseModel):
    group = models.ForeignKey(
        Group,
        verbose_name="Group that has lesson",
        on_delete=models.CASCADE,
        related_name='group',
    )
    lesson = models.ForeignKey(
        Lesson,
        verbose_name="Lesson for the group",
        on_delete=models.CASCADE,
        related_name='lesson',
    )
    subgroup = models.CharField(
        verbose_name="Subgroup of the group that has lesson",
        max_length=1,
        choices=Subgroup,
        null=True,
        blank=True,
    )

    @classmethod
    def from_entity(cls, entity: GroupLessonEntity) -> 'GroupLesson':
        return cls(
            group_id=entity.group.id,
            lesson_id=entity.lesson.id,
            subgroup=entity.subgroup,
        )

    class Meta:
        verbose_name = "Group Lessons"
        verbose_name_plural = "Groups Lessons"
