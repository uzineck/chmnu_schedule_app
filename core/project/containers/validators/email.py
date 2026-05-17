import punq

from core.apps.common.authentication.validators.email import (
    BaseEmailValidatorService,
    ComposedEmailValidatorService,
    EmailAlreadyInUseValidatorService,
    SimilarOldAndNewEmailValidatorService,
)


def register_email_validators(container: punq.Container):
    container.register(SimilarOldAndNewEmailValidatorService)
    container.register(EmailAlreadyInUseValidatorService)

    def build_email_validators() -> BaseEmailValidatorService:
        return ComposedEmailValidatorService(
            validators=[
                container.resolve(SimilarOldAndNewEmailValidatorService),
                container.resolve(EmailAlreadyInUseValidatorService),
            ],
        )

    container.register(BaseEmailValidatorService, factory=build_email_validators)
