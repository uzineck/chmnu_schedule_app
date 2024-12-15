import punq

from core.apps.schedule.validators.group_lesson import BaseGroupLessonValidatorService, \
    CheckGroupHasSubgroupValidatorService, ClientDoesNotMatchRolesValidatorService, \
    CheckLessonInGroupAlreadyExistsValidatorService, ComposedGroupLessonValidatorService


def register_group_lesson_validators(container: punq.Container):
    container.register(CheckGroupHasSubgroupValidatorService)
    container.register(ClientDoesNotMatchRolesValidatorService)
    container.register(CheckLessonInGroupAlreadyExistsValidatorService)

    def build_group_lesson_validators() -> BaseGroupLessonValidatorService:
        return ComposedGroupLessonValidatorService(
            validators=[
                container.resolve(CheckGroupHasSubgroupValidatorService),
                container.resolve(ClientDoesNotMatchRolesValidatorService),
                container.resolve(CheckLessonInGroupAlreadyExistsValidatorService),
            ],
        )

    container.register(BaseGroupLessonValidatorService, factory=build_group_lesson_validators)
