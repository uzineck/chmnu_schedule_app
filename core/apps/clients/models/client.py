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
        max_length=255,
        unique=True,
        blank=False,
    )
    password = models.CharField(
        max_length=250,
        blank=False,
        null=False,
    )
    access_token = models.CharField(
        verbose_name="Client's Access Token",
        max_length=555,
        default=uuid4,
    )
    refresh_token = models.CharField(
        verbose_name="Client's Refresh Token",
        max_length=555,
        default=uuid4,
    )

    def to_entity(self) -> ClientEntity:
        return ClientEntity(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            middle_name=self.middle_name,
            role=ClientRole(self.role),
            email=self.email,
            password=self.password,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def __str__(self):
        return f"{self.last_name} {self.first_name[0]}. {self.middle_name[0]}."

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
