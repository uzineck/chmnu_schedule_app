from django.db import models

import uuid

from core.apps.clients.models.client import Client
from core.apps.common.models import TimedBaseModel
from core.apps.schedule.entities.group import Group as GroupEntity


class Group(TimedBaseModel):
    group_uuid = models.UUIDField(
        verbose_name='UUID group representation',
        editable=False,
        default=uuid.uuid4,
    )
    number = models.CharField(
        verbose_name="Group Number",
        max_length=10,
        unique=True,
    )
    has_subgroups = models.BooleanField(
        verbose_name="Does group has subgroups",
        default=True,
    )
    headman = models.ForeignKey(
        Client,
        verbose_name="Headman of the group",
        related_name='group_headman',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    def to_entity(self) -> GroupEntity:
        return GroupEntity(
            id=self.id,
            uuid=str(self.group_uuid),
            number=self.number,
            has_subgroups=self.has_subgroups,
            headman=self.headman.to_entity(),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Groups"

