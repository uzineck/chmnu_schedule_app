from uuid import uuid4

from django.db import models

from core.apps.common.models import TimedBaseModel
from core.apps.clients.entities.sophomore import Sophomore as SophomoreEntity


class Sophomore(TimedBaseModel):
    first_name = models.CharField(
        verbose_name="Sophomore's First Name",
        max_length=100,
    )
    last_name = models.CharField(
        verbose_name="Sophomore's Last name",
        max_length=100,
    )
    middle_name = models.CharField(
        verbose_name="Sophomore's Middle Name",
        max_length=100,
    )
    email = models.EmailField(
        verbose_name="Sophomore`s email for auth",
        unique=True,
        blank=False,
    )
    password = models.CharField(
        max_length=250,
        blank=False,
        null=False
    )
    token = models.CharField(
        verbose_name="Sophomore's Token",
        max_length=255,
        default=uuid4,
        unique=True,
    )

    def to_entity(self) -> SophomoreEntity:
        return SophomoreEntity(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            middle_name=self.middle_name,
            email=self.email,
            password=self.password,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"

    class Meta:
        verbose_name = "Sophomore"
        verbose_name_plural = "Sophomores"
