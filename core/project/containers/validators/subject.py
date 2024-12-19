import punq

from core.apps.schedule.validators.subject import (
    BaseSubjectValidatorService,
    ComposedSubjectValidatorService,
    SimilarOldAndNewSubjectTitlesValidatorService,
    SubjectAlreadyExistsValidatorService,
)


def register_subject_validators(container: punq.Container):
    container.register(SubjectAlreadyExistsValidatorService)
    container.register(SimilarOldAndNewSubjectTitlesValidatorService)

    def build_subject_validators() -> BaseSubjectValidatorService:
        return ComposedSubjectValidatorService(
            validators=[
                container.resolve(SimilarOldAndNewSubjectTitlesValidatorService),
                container.resolve(SubjectAlreadyExistsValidatorService),
            ],
        )

    container.register(BaseSubjectValidatorService, factory=build_subject_validators)
