from django.db import models

import uuid

from core.apps.common.models import TimedBaseModel
from core.apps.schedule.entities.room import Room as RoomEntity


class Room(TimedBaseModel):
    room_uuid = models.UUIDField(
        verbose_name='UUID room representation',
        editable=False,
        default=uuid.uuid4,
    )
    number = models.CharField(
        verbose_name="Number of the room",
        max_length=20,
        unique=True,
    )
    description = models.CharField(
        verbose_name="Description of the room",
        max_length=300,
        blank=True,
        null=True,
    )

    def to_entity(self) -> RoomEntity:
        return RoomEntity(
            id=self.id,
            uuid=str(self.room_uuid),
            number=self.number,
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = "Room"
        verbose_name_plural = "Rooms"
        indexes = [
            models.Index(fields=["room_uuid"]),
            models.Index(fields=["number"]),
        ]
