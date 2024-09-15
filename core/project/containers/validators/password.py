import punq

from core.apps.common.authentication.validators.password import (
    BasePasswordValidatorService,
    ComposedPasswordValidatorService,
    MatchingVerifyPasswordsValidatorService,
    PasswordPatternValidatorService,
    SimilarOldAndNewPasswordValidatorService,
)


def register_password_validators(container: punq.Container):
    container.register(MatchingVerifyPasswordsValidatorService)
    container.register(PasswordPatternValidatorService)
    container.register(SimilarOldAndNewPasswordValidatorService)

    def build_password_validators() -> BasePasswordValidatorService:
        return ComposedPasswordValidatorService(
            validators=[
                container.resolve(MatchingVerifyPasswordsValidatorService),
                container.resolve(PasswordPatternValidatorService),
                container.resolve(SimilarOldAndNewPasswordValidatorService),
            ],
        )

    container.register(BasePasswordValidatorService, factory=build_password_validators)


