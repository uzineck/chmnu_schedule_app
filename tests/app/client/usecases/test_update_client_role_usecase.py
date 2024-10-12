import pytest
from tests.fixtures.client.client import ClientModelFactory

from core.apps.clients.usecases.client.update_role import UpdateClientRoleUseCase
from core.apps.common.models import ClientRole


@pytest.fixture
def use_case(container):
    return container.resolve(UpdateClientRoleUseCase)


@pytest.fixture(scope='function')
def use_case_params():
    new_role = ClientRole.HEADMAN
    client = ClientModelFactory.create()
    return {
        "email": client.email,
        "new_role": new_role,
    }


@pytest.mark.django_db
def test_update_client_role_success(use_case: UpdateClientRoleUseCase, use_case_params):
    updated_client, tokens = use_case.execute(**use_case_params)

    assert updated_client.role == use_case_params['new_role']
    assert tokens.access_token is not None
    assert tokens.refresh_token is not None
