from django.db import models

import uuid

from core.apps.clients.models.client import Client
from core.apps.common.models import (
    SoftDeletable,
    Subgroup,
    TimedBaseModel,
)
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.entities.group_lessons import GroupLesson as GroupLessonEntity
from core.apps.schedule.models.faculty import Faculty
from core.apps.schedule.models.lesson import Lesson


class Group(TimedBaseModel, SoftDeletable):
    group_uuid = models.UUIDField(
        verbose_name='UUID group representation',
        editable=False,
        default=uuid.uuid4,
        unique=True,
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
    schedule_updated_at = models.DateTimeField(
        verbose_name="Last schedule change time",
        null=True,
        blank=True,
    )

    def to_entity(self) -> GroupEntity:
        return GroupEntity(
            id=self.id,
            uuid=str(self.group_uuid),
            number=self.number,
            faculty=self.faculty.to_entity() if self.faculty_id is not None else None,
            has_subgroups=self.has_subgroups,
            headman=self.headman.to_entity() if self.headman_id is not None else None,
            schedule_updated_at=self.schedule_updated_at,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Groups"


class GroupLesson(TimedBaseModel):
    group = models.ForeignKey(
        Group,
        verbose_name="Group that has lesson",
        on_delete=models.CASCADE,
        related_name='group_lessons',
    )
    lesson = models.ForeignKey(
        Lesson,
        verbose_name="Lesson for the group",
        on_delete=models.CASCADE,
        related_name='lesson_groups',
    )
    subgroup = models.CharField(
        verbose_name="Subgroup of the group that has lesson",
        max_length=1,
        choices=Subgroup,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.group} — {self.lesson} ({self.subgroup or 'no subgroup'})"

    @classmethod
    def from_entity(cls, entity: GroupLessonEntity) -> 'GroupLesson':
        return cls(
            group_id=entity.group.id,
            lesson_id=entity.lesson.id,
            subgroup=entity.subgroup,
        )

    class Meta:
        verbose_name = "Group Lesson"
        verbose_name_plural = "Group Lessons"
        constraints = [
            models.UniqueConstraint(
                fields=['group', 'lesson', 'subgroup'],
                name='unique_group_lesson_subgroup',
                nulls_distinct=False,
            ),
        ]
