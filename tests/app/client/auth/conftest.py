import pytest
from types import SimpleNamespace

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.common.authentication.token import BaseTokenService
from core.apps.common.models import ClientRole


@pytest.fixture
def mock_request():
    return SimpleNamespace()


@pytest.fixture
def client_with_role(client_create, role_create):
    def _build(role: ClientRole = ClientRole.HEADMAN):
        client_model = client_create(roles=[role_create(id=role)])
        client_entity = ClientEntity(
            id=client_model.id,
            first_name=client_model.first_name,
            last_name=client_model.last_name,
            email=client_model.email,
            middle_name=client_model.middle_name,
            roles=[ClientRole(r.id) for r in client_model.roles.all()],
        )
        return client_model, client_entity
    return _build


@pytest.fixture
def valid_access_token(
        token_service: BaseTokenService,
        generate_device_id,
        client_with_role,
):
    def _build(role: ClientRole = ClientRole.HEADMAN):
        _, client_entity = client_with_role(role)
        token = token_service.create_access_token(
            client=client_entity,
            payload={"device_id": generate_device_id},
        )
        return client_entity, token
    return _build
