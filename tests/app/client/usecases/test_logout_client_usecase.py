import pytest
from tests.fixtures.client.client import ClientModelFactory

from core.apps.clients.exceptions.client import ClientEmailNotFoundException
from core.apps.clients.usecases.client.logout import LogoutClientUseCase


@pytest.fixture
def use_case(container):
    return container.resolve(LogoutClientUseCase)


@pytest.fixture(scope='function')
def use_case_params(token_service, generate_device_id):
    client = ClientModelFactory.create()
    payload = {"device_id": generate_device_id}
    access_token = token_service.create_access_token(client=client, payload=payload)
    return {
        "token": access_token,
    }


@pytest.mark.django_db
def test_logout_client_success(use_case: LogoutClientUseCase, use_case_params):
    assert use_case.execute(**use_case_params) is None


@pytest.mark.django_db
def test_logout_client_not_found_failure(
        use_case: LogoutClientUseCase,
        token_service,
        generate_device_id,
):
    client = ClientModelFactory.build()
    payload = {"device_id": generate_device_id}
    access_token = token_service.create_access_token(client=client, payload=payload)

    with pytest.raises(ClientEmailNotFoundException):
        use_case.execute(token=access_token)
