import punq

from core.apps.schedule.validators.room import (
    BaseRoomValidatorService,
    ComposedRoomValidatorService,
    RoomAlreadyExistsValidatorService,
    SimilarOldAndNewRoomDescriptionValidatorService,
    SimilarOldAndNewRoomValidatorService,
)


def register_room_validators(container: punq.Container):
    container.register(RoomAlreadyExistsValidatorService)
    container.register(SimilarOldAndNewRoomValidatorService)
    container.register(SimilarOldAndNewRoomDescriptionValidatorService)

    def build_room_validators() -> BaseRoomValidatorService:
        return ComposedRoomValidatorService(
            validators=[
                container.resolve(RoomAlreadyExistsValidatorService),
                container.resolve(SimilarOldAndNewRoomValidatorService),
                container.resolve(SimilarOldAndNewRoomDescriptionValidatorService),
            ],
        )

    container.register(BaseRoomValidatorService, factory=build_room_validators)
