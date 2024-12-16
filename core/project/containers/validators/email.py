import punq

from core.apps.common.authentication.validators.email import (
    BaseEmailValidatorService,
    ComposedEmailValidatorService,
    EmailAlreadyInUseValidatorService,
    EmailPatternValidatorService,
    SimilarOldAndNewEmailValidatorService,
)


def register_email_validators(container: punq.Container):
    container.register(EmailPatternValidatorService)
    container.register(SimilarOldAndNewEmailValidatorService)
    container.register(EmailAlreadyInUseValidatorService)

    def build_email_validators() -> BaseEmailValidatorService:
        return ComposedEmailValidatorService(
            validators=[
                container.resolve(EmailPatternValidatorService),
                container.resolve(SimilarOldAndNewEmailValidatorService),
                container.resolve(EmailAlreadyInUseValidatorService),
            ],
        )

    container.register(BaseEmailValidatorService, factory=build_email_validators)
