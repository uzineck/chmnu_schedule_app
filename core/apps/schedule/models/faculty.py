from django.db import models

import uuid

from core.apps.common.models import (
    SoftDeletable,
    TimedBaseModel,
)
from core.apps.schedule.entities.faculty import Faculty as FacultyEntity


class Faculty(TimedBaseModel, SoftDeletable):
    faculty_uuid = models.UUIDField(
        verbose_name='UUID faculty representation',
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    code_name = models.CharField(
        verbose_name='Code name of the faculty',
        max_length=20,
        unique=True,
    )
    name = models.CharField(
        verbose_name='Name of the faculty',
        max_length=100,
    )

    def to_entity(self) -> FacultyEntity:
        return FacultyEntity(
            id=self.id,
            uuid=str(self.faculty_uuid),
            code_name=self.code_name,
            name=self.name,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def __str__(self):
        return self.code_name

    class Meta:
        verbose_name = 'Faculty'
        verbose_name_plural = 'Faculties'
