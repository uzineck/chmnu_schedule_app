from django.db import models

import uuid

from core.apps.common.models import (
    SoftDeletable,
    TeachersDegree,
    TimedBaseModel,
)
from core.apps.schedule.entities.teacher import Teacher as TeacherEntity


class Teacher(TimedBaseModel, SoftDeletable):
    teacher_uuid = models.UUIDField(
        verbose_name='UUID teacher representation',
        editable=False,
        default=uuid.uuid4,
        unique=True,
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
        max_length=30,
    )

    def to_entity(self) -> TeacherEntity:
        return TeacherEntity(
            id=self.id,
            uuid=str(self.teacher_uuid),
            first_name=self.first_name,
            last_name=self.last_name,
            middle_name=self.middle_name,
            rank=self.rank,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def __str__(self):
        initials = " ".join(
            name[0] + "." for name in [self.first_name, self.middle_name] if name
        )
        return f"{self.last_name} {initials}".strip()

    class Meta:
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"
