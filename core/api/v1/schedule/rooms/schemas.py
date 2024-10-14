from ninja import Schema

from typing import Optional

from core.apps.schedule.entities.room import Room as RoomEntity


class RoomSchema(Schema):
    uuid: str
    number: str
    description: Optional[str] = None

    @classmethod
    def from_entity(cls, entity: RoomEntity) -> 'RoomSchema':
        return cls(
            uuid=entity.uuid,
            number=entity.number,
            description=entity.description,
        )


class RoomNumberInSchema(Schema):
    number: str


class RoomDescriptionInSchema(Schema):
    description: str
