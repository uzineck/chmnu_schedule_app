import datetime as dt
from django.db import models

from core.apps.schedule.models.rooms import Room
from core.apps.schedule.models.subjects import Subject
from core.apps.schedule.models.teachers import Teacher
from core.apps.schedule.models.timeslots import Timeslot
from core.apps.common.models import TimedBaseModel, LessonType, Subgroup


class Lesson(TimedBaseModel):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        verbose_name="Subject of the lesson",
        related_name='lesson_subject',
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.PROTECT,
        verbose_name="Teacher that holds the lesson",
        related_name="lesson_teacher",
    )
    type = models.CharField(
        verbose_name="Type of the lesson",
        choices=LessonType,
        max_length=10,
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        verbose_name="Room where the lesson is held",
        related_name='lesson_room',
    )
    timeslot = models.ForeignKey(
        Timeslot,
        on_delete=models.PROTECT,
        verbose_name="Timeslot when the lesson is held",
        related_name='lesson_timeslot',
    )
    subgroup = models.CharField(
        max_length=1,
        choices=Subgroup,
        null=True,
    )

    def __str__(self):
        return (f"Lesson: {self.type} {self.subject}, "
                f"Teacher: {self.teacher}, "
                f"Day: {self.timeslot.day}, "
                f"Number: {self.timeslot.ord_number}, "
                f"Subgroup: {self.subgroup}")

    def save(self, *args, **kwargs):
        existing_timeslot = Timeslot.objects.filter(
            day=self.timeslot.day,
            ord_number=self.timeslot.ord_number,
            is_even=self.timeslot.is_even
        ).first()
        if existing_timeslot:
            self.timeslot = existing_timeslot
        else:
            self.timeslot.save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"
