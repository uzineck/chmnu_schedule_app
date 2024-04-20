from typing import Optional

from ninja import Schema

from core.apps.schedule.entities.room import Room as RoomEntity


class RoomSchema(Schema):
    number: str
    description: Optional[str] = None

    @staticmethod
    def from_entity(entity: RoomEntity) -> 'RoomSchema':
        return RoomSchema(
            number=entity.number,
            description=entity.description
        )


class RoomNumberInSchema(Schema):
    number: str


class RoomDescriptionUpdateInSchema(Schema):
    description: str

