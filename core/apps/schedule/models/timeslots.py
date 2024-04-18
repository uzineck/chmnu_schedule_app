from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from core.apps.common.models import TimedBaseModel, Day, OrdinaryNumber
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
            day=self.day,
            ord_number=self.ord_number,
            is_even=self.is_even,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    def __str__(self):
        return (f"{self.day}\n"
                f"{self.ord_number}\n"
                f"{str(self.is_even)}")

    class Meta:
        verbose_name = "Timeslot"
        verbose_name_plural = "Timeslots"


@receiver(pre_save, sender=Timeslot)
def check_existing_timeslot(sender, instance, **kwargs):
    existing_timeslot = Timeslot.objects.filter(
        day=instance.day,
        ord_number=instance.ord_number,
        is_even=instance.is_even
    ).first()
    if existing_timeslot:
        instance.created_at = existing_timeslot.created_at
        instance.updated_at = existing_timeslot.updated_at
        instance.id = existing_timeslot.id
