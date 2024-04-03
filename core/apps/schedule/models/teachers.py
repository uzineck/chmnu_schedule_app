from django.db import models

from core.apps.common.models import TimedBaseModel
from core.apps.common.models import TeachersDegree
from core.apps.schedule.models.subjects import Subject


class Teacher(TimedBaseModel):
    first_name = models.CharField(
        verbose_name="Teacher's First Name",
        max_length=100,
    )
    last_name = models.CharField(
        verbose_name="Teacher's last name",
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
        related_name='teacher_subjects'
    )
    is_active = models.BooleanField(
        verbose_name="Is teacher still teaching",
        default=True
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name[0]}. {self.middle_name[0]}."

    class Meta:
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"

