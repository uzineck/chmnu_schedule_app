import datetime

from django.db import models

from core.apps.common.models import TimedBaseModel


class SemesterSettings(TimedBaseModel):
    start_date = models.DateField(
        verbose_name='Start of the current academic semester',
    )
    is_above_line = models.BooleanField(
        verbose_name='Is the first week of the semester above the line',
        default=True,
    )

    def save(self, *args, **kwargs):
        self.pk = 1
        if self.created_at is None:
            existing_created_at = type(self).objects.filter(pk=1).values_list(
                'created_at', flat=True,
            ).first()
            if existing_created_at is not None:
                self.created_at = existing_created_at
        super().save(*args, **kwargs)

    @classmethod
    def get_singleton(cls) -> 'SemesterSettings':
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                'start_date': datetime.date(2024, 9, 2),
                'is_above_line': True,
            },
        )
        return obj

    def __str__(self) -> str:
        return f'Semester start: {self.start_date} (above_line={self.is_above_line})'

    class Meta:
        verbose_name = 'Semester Settings'
        verbose_name_plural = 'Semester Settings'
