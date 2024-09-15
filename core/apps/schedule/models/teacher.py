from django.db import models

import uuid

from core.apps.common.models import (
    TeachersDegree,
    TimedBaseModel,
)
from core.apps.schedule.entities.teacher import Teacher as TeacherEntity
from core.apps.schedule.models.subject import Subject


class Teacher(TimedBaseModel):
    teacher_uuid = models.UUIDField(
        verbose_name='UUID teacher representation',
        editable=False,
        default=uuid.uuid4,
    )
    first_name = models.CharField(
        verbose_name="Teacher's First Name",
        max_length=100,
    )
    last_name = models.CharField(
        verbose_name="Teacher's Last name",
        max_length=100,
    )
    middle_name = models.CharField(
        verbose_name="Teacher's Middle Name",
        max_length=100,
    )
    rank = models.CharField(
        verbose_name="Teacher's rank",
        choices=TeachersDegree,
    )
    subjects = models.ManyToManyField(
        Subject,
        related_name='teacher_subjects',
        blank=True,
    )
    is_active = models.BooleanField(
        verbose_name="Is teacher still teaching",
        default=True,
    )

    def to_entity(self) -> TeacherEntity:
        return TeacherEntity(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            middle_name=self.middle_name,
            rank=self.rank,
            subjects=self.subjects,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def __str__(self):
        return f"{self.last_name} {self.first_name[0]}. {self.middle_name[0]}."

    class Meta:
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"

