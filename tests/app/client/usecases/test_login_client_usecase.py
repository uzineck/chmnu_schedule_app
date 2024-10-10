import pytest
from tests.app.auth.password.conftest import hash_password
from tests.fixtures.client.client import ClientModelFactory
from tests.fixtures.client.utils import (
    generate_email,
    generate_password,
)

from core.apps.clients.exceptions.auth import InvalidAuthDataException
from core.apps.clients.usecases.client.login import LoginClientUseCase


@pytest.fixture
def use_case(container):
    return container.resolve(LoginClientUseCase)


@pytest.fixture(scope='function')
def use_case_params(password_service):
    plain_password = generate_password()
    hashed_password = hash_password(password_service=password_service, plain_password=plain_password)
    client = ClientModelFactory.create(password=hashed_password)
    return {
        "email": client.email,
        "password": plain_password,
    }


@pytest.mark.django_db
def test_login_client_success(use_case: LoginClientUseCase, use_case_params):
    logged_in_data = use_case.execute(**use_case_params)
    client, tokens = logged_in_data

    assert client.email == use_case_params['email']
    assert client.password != use_case_params['password']
    assert tokens.access_token is not None
    assert tokens.refresh_token is not None


@pytest.mark.django_db
def test_login_client_does_not_exist_failure(use_case: LoginClientUseCase, use_case_params):
    use_case_params = use_case_params
    use_case_params['email'] = generate_email()

    with pytest.raises(InvalidAuthDataException):
        use_case.execute(**use_case_params)


@pytest.mark.django_db
def test_login_client_wrong_password_failure(use_case: LoginClientUseCase, use_case_params):
    use_case_params = use_case_params
    use_case_params['password'] = generate_password()

    with pytest.raises(InvalidAuthDataException):
        use_case.execute(**use_case_params)
