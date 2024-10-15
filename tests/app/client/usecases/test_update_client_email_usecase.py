import pytest
from tests.fixtures.client.client import ClientModelFactory

from core.apps.clients.exceptions.auth import InvalidAuthDataException
from core.apps.clients.exceptions.client import ClientNotFoundException
from core.apps.clients.usecases.client.update_email import UpdateClientEmailUseCase
from core.apps.common.authentication.validators.exceptions import (
    InvalidEmailPatternException,
    OldAndNewEmailsAreSimilarException,
)


@pytest.fixture
def use_case(container):
    return container.resolve(UpdateClientEmailUseCase)


@pytest.fixture(scope='function')
def use_case_params(generate_email, generate_password, hash_password):
    new_email = generate_email()
    plain_password = generate_password()
    hashed_password = hash_password(plain_password)
    client = ClientModelFactory.create(password=hashed_password)
    return {
        "old_email": client.email,
        "new_email": new_email,
        "password": plain_password,
    }


@pytest.mark.django_db
def test_update_client_email_success(use_case: UpdateClientEmailUseCase, use_case_params):
    updated_client, tokens = use_case.execute(**use_case_params)

    assert updated_client.email != use_case_params['old_email']
    assert tokens.access_token is not None
    assert tokens.refresh_token is not None


@pytest.mark.django_db
def test_update_client_email_email_not_found_failure(use_case: UpdateClientEmailUseCase, use_case_params):
    client = ClientModelFactory.build()

    with pytest.raises(ClientNotFoundException):
        use_case.execute(
            old_email=client.email,
            new_email=use_case_params['new_email'],
            password=use_case_params['password'],
        )


@pytest.mark.django_db
def test_update_client_email_password_verification_failure(
        use_case: UpdateClientEmailUseCase,
        use_case_params,
        generate_password,
):
    with pytest.raises(InvalidAuthDataException):
        use_case.execute(
            old_email=use_case_params['old_email'],
            new_email=use_case_params['new_email'],
            password=generate_password(),
        )


@pytest.mark.django_db
def test_update_client_email_new_email_pattern_validation_failure(
        use_case: UpdateClientEmailUseCase,
        use_case_params,
):
    with pytest.raises(InvalidEmailPatternException):
        use_case.execute(
            old_email=use_case_params['old_email'],
            new_email=use_case_params['new_email'][:7],
            password=use_case_params['password'],
        )


@pytest.mark.django_db
def test_update_client_email_new_email_similar_validation_failure(
        use_case: UpdateClientEmailUseCase,
        use_case_params,
):
    with pytest.raises(OldAndNewEmailsAreSimilarException):
        use_case.execute(
            old_email=use_case_params['old_email'],
            new_email=use_case_params['old_email'],
            password=use_case_params['password'],
        )
