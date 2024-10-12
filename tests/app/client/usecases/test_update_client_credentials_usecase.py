import pytest
from tests.fixtures.client.client import ClientModelFactory

from core.apps.clients.exceptions.client import ClientEmailNotFoundException
from core.apps.clients.usecases.client.update_credentials import UpdateClientCredentialsUseCase


@pytest.fixture
def use_case(container):
    return container.resolve(UpdateClientCredentialsUseCase)


@pytest.fixture(scope='function')
def use_case_params(faker_ua):
    first_name = faker_ua.first_name()
    last_name = faker_ua.last_name()
    middle_name = faker_ua.middle_name()
    client = ClientModelFactory.create()
    return {
        "email": client.email,
        "first_name": first_name,
        "last_name": last_name,
        "middle_name": middle_name,
    }


@pytest.mark.django_db
def test_update_client_credentials_success(use_case: UpdateClientCredentialsUseCase, use_case_params):
    updated_client = use_case.execute(**use_case_params)

    assert updated_client.first_name == use_case_params['first_name']
    assert updated_client.last_name == use_case_params['last_name']
    assert updated_client.middle_name == use_case_params['middle_name']
    assert updated_client.email == use_case_params['email']


@pytest.mark.django_db
def test_update_credentials_client_not_found_failure(use_case: UpdateClientCredentialsUseCase, use_case_params):
    client = ClientModelFactory.build()

    with pytest.raises(ClientEmailNotFoundException):
        use_case.execute(
            email=client.email,
            first_name=use_case_params['first_name'],
            last_name=use_case_params['last_name'],
            middle_name=use_case_params['middle_name'],
        )
