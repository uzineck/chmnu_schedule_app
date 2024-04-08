from django.db import models

from core.apps.common.models import TimedBaseModel


class Room(TimedBaseModel):
    number = models.CharField(
        verbose_name="Number of the room",
        max_length=20,
        unique=True,
    )
    description = models.CharField(
        verbose_name="Description of the room",
        max_length=300,
        blank=True
    )

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = "Room"
        verbose_name_plural = "Rooms"
