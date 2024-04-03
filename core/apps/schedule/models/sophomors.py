from uuid import uuid4

from django.db import models

from core.apps.common.models import TimedBaseModel


class Sophomore(TimedBaseModel):
    first_name = models.CharField(
        verbose_name="Sophomore's First Name",
        max_length=100,
    )
    last_name = models.CharField(
        verbose_name="Sophomore's last name",
        max_length=100,
    )
    middle_name = models.CharField(
        verbose_name="Sophomore's Middle Name",
        max_length=100,
    )
    token = models.CharField(
        verbose_name="Sophomore's Token",
        max_length=255,
        default=uuid4,
        unique=True,
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.middle_name}"

    class Meta:
        verbose_name = "Sophomore"
        verbose_name_plural = "Sophomores"
