import pytest
from tests.factories.client.client import ClientModelFactory
from tests.factories.client.role import RoleModelFactory

from core.apps.clients.exceptions.client import ClientNotFoundException
from core.apps.clients.usecases.admin.update_role import UpdateClientRoleUseCase
from core.apps.common.models import ClientRole


@pytest.fixture
def use_case(container):
    return container.resolve(UpdateClientRoleUseCase)


@pytest.fixture(scope='function')
def use_case_params():
    roles = [ClientRole.HEADMAN, ClientRole.CLIENT_MANAGER]
    client = ClientModelFactory.create(roles=[RoleModelFactory(id=ClientRole.DEFAULT)])
    return {
        "email": client.email,
        "roles": roles,
    }

#
# @pytest.mark.django_db
# def test_update_client_role_success(use_case: UpdateClientRoleUseCase, use_case_params):
#     updated_client = use_case.execute(**use_case_params)
#
#     assert updated_client.roles == use_case_params['roles']


@pytest.mark.django_db
def test_update_client_role_email_not_found_failure(
        use_case,
        use_case_params,
):
    client = ClientModelFactory.build()

    with pytest.raises(ClientNotFoundException):
        use_case.execute(
            email=client.email,
            roles=use_case_params['roles'],
        )
