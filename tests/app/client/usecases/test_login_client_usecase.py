import pytest
from tests.factories.client.client import ClientModelFactory

from core.apps.clients.exceptions.auth import InvalidAuthDataException
from core.apps.clients.exceptions.client import ClientNotFoundException
from core.apps.clients.usecases.client.login import LoginClientUseCase


@pytest.fixture
def use_case(container):
    return container.resolve(LoginClientUseCase)


@pytest.fixture(scope='function')
def use_case_params(generate_password, hash_password):
    plain_password = generate_password()
    hashed_password = hash_password(plain_password=plain_password)
    client = ClientModelFactory.create(password=hashed_password)
    return {
        "email": client.email,
        "password": plain_password,
    }


@pytest.mark.django_db
def test_login_client_success(use_case: LoginClientUseCase, use_case_params):
    client, tokens = use_case.execute(**use_case_params)

    assert client.email == use_case_params['email']
    assert client.password != use_case_params['password']
    assert tokens.access_token is not None
    assert tokens.refresh_token is not None


@pytest.mark.django_db
def test_login_client_does_not_exist_failure(use_case: LoginClientUseCase, use_case_params, generate_email):
    use_case_params = use_case_params
    use_case_params['email'] = generate_email()

    with pytest.raises(ClientNotFoundException):
        use_case.execute(**use_case_params)


@pytest.mark.django_db
def test_login_client_wrong_password_failure(use_case: LoginClientUseCase, use_case_params, generate_password):
    use_case_params = use_case_params
    use_case_params['password'] = generate_password()

    with pytest.raises(InvalidAuthDataException):
        use_case.execute(**use_case_params)
