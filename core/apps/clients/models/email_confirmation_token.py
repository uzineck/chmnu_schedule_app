from django.db import models

import uuid

from core.apps.clients.entities.email_confirmation_token import (
    ClientEmailConfirmationToken as ClientEmailConfirmationTokenEntity,
)
from core.apps.clients.models.client import Client
from core.apps.common.models import TimedBaseModel


class ClientEmailConfirmationToken(TimedBaseModel):
    token = models.UUIDField(
        verbose_name='One-time confirmation token',
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    client = models.ForeignKey(
        Client,
        verbose_name='Client this token belongs to',
        on_delete=models.CASCADE,
        related_name='email_confirmation_tokens',
    )
    expires_at = models.DateTimeField(
        verbose_name='Expiration time',
    )
    used_at = models.DateTimeField(
        verbose_name='When the token was used (consumed)',
        null=True,
        blank=True,
    )

    def to_entity(self) -> ClientEmailConfirmationTokenEntity:
        return ClientEmailConfirmationTokenEntity(
            id=self.id,
            token=str(self.token),
            client=self.client.to_entity(),
            expires_at=self.expires_at,
            used_at=self.used_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def __str__(self) -> str:
        return f'{self.client}: {self.token}'

    class Meta:
        verbose_name = 'Client Email Confirmation Token'
        verbose_name_plural = 'Client Email Confirmation Tokens'
        indexes = [
            models.Index(fields=['token']),
        ]
