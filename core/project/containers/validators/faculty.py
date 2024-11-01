import punq

from core.apps.schedule.validators.faculty import (
    BaseFacultyValidatorService,
    ComposedFacultyValidatorService,
    FacultyAlreadyExistsByCodeNameValidatorService,
    FacultyAlreadyExistsByNameValidatorService,
    SimilarOldAndNewFacultyCodeNameValidatorService,
    SimilarOldAndNewFacultyNameValidatorService,
)


def register_faculty_validators(container: punq.Container):
    container.register(FacultyAlreadyExistsByNameValidatorService)
    container.register(FacultyAlreadyExistsByCodeNameValidatorService)
    container.register(SimilarOldAndNewFacultyNameValidatorService)
    container.register(SimilarOldAndNewFacultyCodeNameValidatorService)

    def build_faculty_validators() -> BaseFacultyValidatorService:
        return ComposedFacultyValidatorService(
            validators=[
                container.resolve(FacultyAlreadyExistsByNameValidatorService),
                container.resolve(FacultyAlreadyExistsByCodeNameValidatorService),
                container.resolve(SimilarOldAndNewFacultyNameValidatorService),
                container.resolve(SimilarOldAndNewFacultyCodeNameValidatorService),
            ],
        )

    container.register(BaseFacultyValidatorService, factory=build_faculty_validators)
