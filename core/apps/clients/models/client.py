from django.db import models

from uuid import uuid4

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.common.models import (
    ClientRole,
    TimedBaseModel,
)


class Client(TimedBaseModel):
    first_name = models.CharField(
        verbose_name="Client's First Name",
        max_length=100,
    )
    last_name = models.CharField(
        verbose_name="Client's Last name",
        max_length=100,
    )
    middle_name = models.CharField(
        verbose_name="Client's Middle Name",
        max_length=100,
    )
    role = models.CharField(
        verbose_name="Client's role",
        choices=ClientRole,
        default=ClientRole.DEFAULT,
    )
    email = models.EmailField(
        verbose_name="Client's email for auth",
        unique=True,
        blank=False,
    )
    password = models.CharField(
        max_length=250,
        blank=False,
        null=False,
    )
    token = models.CharField(
        verbose_name="Client's Token",
        max_length=255,
        default=uuid4,
        unique=True,
    )

    def to_entity(self) -> ClientEntity:
        return ClientEntity(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            middle_name=self.middle_name,
            role=self.role,
            email=self.email,
            password=self.password,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
