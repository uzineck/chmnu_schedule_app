from django.db import models

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.models.role import Role
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
    roles = models.ManyToManyField(
        Role,
        verbose_name="Client's Roles",
        related_name="clients",
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

    def to_entity(self) -> ClientEntity:
        return ClientEntity(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            middle_name=self.middle_name,
            roles=[ClientRole(role.id) for role in self.roles.all()],
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
        indexes = [
            models.Index(fields=["email"]),
        ]
