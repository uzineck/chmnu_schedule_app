from django.db import models

import uuid

from core.apps.common.models import TimedBaseModel


class Faculty(TimedBaseModel):
    faculty_uuid = models.UUIDField(
        verbose_name='UUID faculty representation',
        default=uuid.uuid4,
        editable=False,
    )
    code_name = models.CharField(
        verbose_name='Code name of the faculty',
        max_length=10,
        unique=True,
    )
    name = models.CharField(
        verbose_name='Name of the faculty',
        max_length=100,
    )

    class Meta:
        verbose_name = 'Faculty'
        verbose_name_plural = 'Faculties'
