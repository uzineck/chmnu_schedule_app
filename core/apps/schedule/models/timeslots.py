from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.apps.common.models import TimedBaseModel, Day, OrdinaryNumber


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

    def __str__(self):
        return (f"{self.day}\n"
                f"{self.ord_number}\n"
                f"{str(self.is_even)}")

    class Meta:
        verbose_name = "Timeslot"
        verbose_name_plural = "Timeslots"
