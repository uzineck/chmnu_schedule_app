import pytest
from tests.factories.client.client import ClientModelFactory

from core.apps.clients.exceptions.client import ClientNotFoundException
from core.apps.clients.usecases.client.logout import LogoutClientUseCase


@pytest.fixture
def use_case(container):
    return container.resolve(LogoutClientUseCase)


@pytest.fixture(scope='function')
def use_case_params(generate_device_id):
    client = ClientModelFactory.create()
    return {
        "client_email": client.email,
        "device_id": generate_device_id,
    }


@pytest.mark.django_db
def test_logout_client_success(use_case: LogoutClientUseCase, use_case_params):
    assert use_case.execute(**use_case_params) is None


@pytest.mark.django_db
def test_logout_client_not_found_failure(
        use_case: LogoutClientUseCase,
        generate_device_id,
):
    client = ClientModelFactory.build()

    with pytest.raises(ClientNotFoundException):
        use_case.execute(client_email=client.email, device_id=generate_device_id)
