from django.db import models

import uuid

from core.apps.common.models import TimedBaseModel
from core.apps.schedule.entities.subject import Subject as SubjectEntity


class Subject(TimedBaseModel):
    subject_uuid = models.UUIDField(
        verbose_name='UUID subject representation',
        editable=False,
        default=uuid.uuid4,
    )
    title = models.CharField(
        verbose_name="Subject's title",
        max_length=150,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name="Subject's slug",
        max_length=150,
    )

    def to_entity(self) -> SubjectEntity:
        return SubjectEntity(
            id=self.id,
            title=self.title,
            slug=self.slug,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"

