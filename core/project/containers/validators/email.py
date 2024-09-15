import punq

from core.apps.common.authentication.validators.email import (
    BaseEmailValidatorService,
    ComposedEmailValidatorService,
    EmailPatternValidatorService,
    SimilarOldAndNewEmailValidatorService,
)


def register_email_validators(container: punq.Container):
    container.register(EmailPatternValidatorService)
    container.register(SimilarOldAndNewEmailValidatorService)

    def build_email_validators() -> BaseEmailValidatorService:
        return ComposedEmailValidatorService(
            validators=[
                container.resolve(EmailPatternValidatorService),
                container.resolve(SimilarOldAndNewEmailValidatorService),
            ],
        )

    container.register(BaseEmailValidatorService, factory=build_email_validators)


