import pytest
from tests.factories.client.client import ClientModelFactory

from core.apps.clients.exceptions.auth import InvalidAuthDataException
from core.apps.clients.exceptions.client import ClientNotFoundException
from core.apps.clients.usecases.client.update_password import UpdateClientPasswordUseCase
from core.apps.common.authentication.validators.exceptions import (
    InvalidPasswordPatternException,
    OldAndNewPasswordsAreSimilarException,
    PasswordsNotMatchingException,
)


@pytest.fixture
def use_case(container):
    return container.resolve(UpdateClientPasswordUseCase)


@pytest.fixture(scope='function')
def use_case_params(generate_password, hash_password):
    original_password = generate_password()
    hashed_password = hash_password(original_password)
    client = ClientModelFactory.create(password=hashed_password)
    new_password = generate_password()
    return {
        "email": client.email,
        "old_password": original_password,
        "new_password": new_password,
        "verify_password": new_password,
    }


@pytest.mark.django_db
def test_update_client_password_success(
        use_case: UpdateClientPasswordUseCase,
        use_case_params,
):
    assert use_case.execute(**use_case_params) is None


@pytest.mark.django_db
def test_update_client_password_email_not_found_failure(
        use_case,
        use_case_params,
):
    client = ClientModelFactory.build()

    with pytest.raises(ClientNotFoundException):
        use_case.execute(
            email=client.email,
            old_password=use_case_params["old_password"],
            new_password=use_case_params["new_password"],
            verify_password=use_case_params["verify_password"],
        )


@pytest.mark.django_db
def test_update_client_password_password_verification_failure(
        use_case,
        use_case_params,
        generate_password,
):
    with pytest.raises(InvalidAuthDataException):
        use_case.execute(
            email=use_case_params["email"],
            old_password=generate_password(),
            new_password=use_case_params["new_password"],
            verify_password=use_case_params["verify_password"],
        )


@pytest.mark.django_db
def test_update_client_password_new_password_pattern_validation_failure(
        use_case,
        use_case_params,
):
    with pytest.raises(InvalidPasswordPatternException):
        use_case.execute(
            email=use_case_params["email"],
            old_password=use_case_params["old_password"],
            new_password=use_case_params["new_password"][:6],
            verify_password=use_case_params["verify_password"][:6],
        )


@pytest.mark.django_db
def test_update_client_password_new_password_not_match_validation_failure(
        use_case,
        use_case_params,
        generate_password,
        hash_password,
):
    with pytest.raises(PasswordsNotMatchingException):
        use_case.execute(
            email=use_case_params["email"],
            old_password=use_case_params["old_password"],
            new_password=use_case_params["new_password"],
            verify_password=generate_password(),
        )


@pytest.mark.django_db
def test_update_client_password_new_password_similar_with_old_one_validation_failure(
        use_case,
        use_case_params,
):
    with pytest.raises(OldAndNewPasswordsAreSimilarException):
        use_case.execute(
            email=use_case_params["email"],
            old_password=use_case_params["old_password"],
            new_password=use_case_params["old_password"],
            verify_password=use_case_params["old_password"],
        )
