import punq

from core.apps.schedule.validators.group import (
    BaseGroupValidatorService,
    ComposedGroupValidatorService,
    GroupAlreadyExistsValidatorService,
    HeadmanAssignedToAnotherGroupValidatorService,
)


def register_group_validators(container: punq.Container):
    container.register(GroupAlreadyExistsValidatorService)
    container.register(HeadmanAssignedToAnotherGroupValidatorService)

    def build_group_validators() -> BaseGroupValidatorService:
        return ComposedGroupValidatorService(
            validators=[
                container.resolve(GroupAlreadyExistsValidatorService),
                container.resolve(HeadmanAssignedToAnotherGroupValidatorService),
            ],
        )

    container.register(BaseGroupValidatorService, factory=build_group_validators)
