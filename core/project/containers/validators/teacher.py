import punq

from core.apps.schedule.validators.teacher import (
    BaseTeacherValidatorService,
    ComposedTeacherValidatorService,
    SimilarOldAndNewTeacherNameValidatorService,
    SimilarOldAndNewTeacherRanksValidatorService,
)


def register_teacher_validators(container: punq.Container):
    container.register(SimilarOldAndNewTeacherNameValidatorService)
    container.register(SimilarOldAndNewTeacherRanksValidatorService)

    def build_teacher_validators() -> BaseTeacherValidatorService:
        return ComposedTeacherValidatorService(
            validators=[
                container.resolve(SimilarOldAndNewTeacherNameValidatorService),
                container.resolve(SimilarOldAndNewTeacherRanksValidatorService),
            ],
        )

    container.register(BaseTeacherValidatorService, factory=build_teacher_validators)
