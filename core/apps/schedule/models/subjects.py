from django.db import models

from core.apps.common.models import TimedBaseModel


class Subject(TimedBaseModel):
    title = models.CharField(
        verbose_name="Subject's title",
        max_length=150,
    )
    slug = models.SlugField(
        verbose_name="Subject's slug",
        max_length=150,
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"

