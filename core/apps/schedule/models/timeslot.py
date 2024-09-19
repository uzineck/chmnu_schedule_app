from django.db import models

from core.apps.common.models import (
    Day,
    OrdinaryNumber,
    TimedBaseModel,
)
from core.apps.schedule.entities.timeslot import Timeslot as TimeslotEntity


class Timeslot(TimedBaseModel):
    day = models.CharField(
        verbose_name="The day of the week for the lesson",
        choices=Day,
        max_length=2,
    )
    ord_number = models.PositiveSmallIntegerField(
        verbose_name='Ordinary number of the lesson',
        choices=OrdinaryNumber,
    )
    is_even = models.BooleanField(
        verbose_name="Is this lesson taken during even weeks",
        default=True,
    )

    def to_entity(self) -> TimeslotEntity:
        return TimeslotEntity(
            id=self.id,
            day=Day(self.day),
            ord_number=OrdinaryNumber(self.ord_number),
            is_even=self.is_even,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def __str__(self):
        return (
            f"{self.day}\n"
            f"{self.ord_number}\n"
            f"{str(self.is_even)}"
        )

    class Meta:
        verbose_name = "Timeslot"
        verbose_name_plural = "Timeslots"
        unique_together = (("day", "ord_number", "is_even"),)
