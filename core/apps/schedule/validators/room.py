from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.schedule.exceptions.room import (
    OldAndNewRoomDescriptionsAreSimilarException,
    OldAndNewRoomsAreSimilarException,
    RoomAlreadyExistException,
)
from core.apps.schedule.services.room import BaseRoomService


class BaseRoomValidatorService(ABC):

    @abstractmethod
    def validate(
            self,
            number: str | None = None,
            description: str | None = None,
            old_number: str | None = None,
            old_description: str | None = None,
    ):
        ...


@dataclass
class RoomAlreadyExistsValidatorService(BaseRoomValidatorService):
    room_service: BaseRoomService

    def validate(self, number: str | None = None, *args, **kwargs):
        if number:
            if self.room_service.check_exists_by_number(room_number=number):
                raise RoomAlreadyExistException(number=number)


class SimilarOldAndNewRoomValidatorService(BaseRoomValidatorService):
    def validate(
            self,
            number: str | None = None,
            old_number: str | None = None,
            *args,
            **kwargs,
    ):
        if number and old_number:
            if number == old_number:
                raise OldAndNewRoomsAreSimilarException(old_number=old_number, new_number=number)


class SimilarOldAndNewRoomDescriptionValidatorService(BaseRoomValidatorService):
    def validate(
            self,
            description: str | None = None,
            old_description: str | None = None,
            *args,
            **kwargs,
    ):
        if description:
            if description == old_description:
                raise OldAndNewRoomDescriptionsAreSimilarException(
                    old_description=old_description,
                    new_description=description,
                )


@dataclass
class ComposedRoomValidatorService(BaseRoomValidatorService):
    validators: list[BaseRoomValidatorService]

    def validate(
            self,
            number: str | None = None,
            description: str | None = None,
            old_number: str | None = None,
            old_description: str | None = None,
    ):
        for validator in self.validators:
            validator.validate(
                number=number,
                description=description,
                old_number=old_number,
                old_description=old_description,
            )
