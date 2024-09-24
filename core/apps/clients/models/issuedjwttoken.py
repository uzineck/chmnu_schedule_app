from django.db import models

from core.apps.clients.models import Client
from core.apps.common.models import TimedBaseModel


class IssuedJwtToken(TimedBaseModel):
    subject = models.ForeignKey(
        Client,
        verbose_name='Tokens subject',
        on_delete=models.CASCADE,
        related_name='issued_jwt_tokens',
    )
    jti = models.UUIDField(
        verbose_name='JWT Token unique ID',
        unique=True,
        editable=False,
    )
    device_id = models.CharField(
        verbose_name='JWT Token device ID',
        max_length=36,
    )
    expiration_time = models.IntegerField(
        verbose_name='UNIX timestamp expiration time of the token',
    )
    revoked = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.subject}: {self.jti}'

    class Meta:
        verbose_name = 'JWT Token'
        verbose_name_plural = 'JWT Tokens'
