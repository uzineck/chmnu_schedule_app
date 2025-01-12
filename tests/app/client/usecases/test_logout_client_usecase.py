import pytest
from tests.factories.client.client import ClientModelFactory

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.exceptions.client import ClientNotFoundException
from core.apps.clients.usecases.client.logout import LogoutClientUseCase
from core.apps.common.models import ClientRole


@pytest.fixture
def use_case(container):
    return container.resolve(LogoutClientUseCase)


@pytest.fixture(scope='function')
def use_case_params(token_service, generate_device_id):
    client = ClientModelFactory.create()
    client_entity = ClientEntity(
        id=client.id,
        first_name=client.first_name,
        last_name=client.last_name,
        email=client.email,
        middle_name=client.middle_name,
        roles=[ClientRole(role.id) for role in client.roles.all()],
    )
    payload = {"device_id": generate_device_id}
    access_token = token_service.create_access_token(client=client_entity, payload=payload)
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
    client_entity = ClientEntity(
        id=client.id,
        first_name=client.first_name,
        last_name=client.last_name,
        email=client.email,
        middle_name=client.middle_name,
        roles=[ClientRole(role.id) for role in client.roles.all()],
    )
    payload = {"device_id": generate_device_id}
    access_token = token_service.create_access_token(client=client_entity, payload=payload)

    with pytest.raises(ClientNotFoundException):
        use_case.execute(token=access_token)
