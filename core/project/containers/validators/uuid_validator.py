import punq

from core.apps.schedule.validators.uuid_validator import (
    BaseUuidValidatorService,
    ComposedUuidValidatorService,
    InvalidUuidTypeValidatorService,
)


def register_uuid_validators(container: punq.Container):
    container.register(InvalidUuidTypeValidatorService)

    def build_uuid_validators() -> BaseUuidValidatorService:
        return ComposedUuidValidatorService(
            validators=[
                container.resolve(InvalidUuidTypeValidatorService),
            ],
        )

    container.register(BaseUuidValidatorService, factory=build_uuid_validators)
