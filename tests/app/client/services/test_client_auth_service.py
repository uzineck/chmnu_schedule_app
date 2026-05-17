import pytest
from tests.factories.client.role import RoleModelFactory

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.exceptions.auth import InvalidAuthDataException
from core.apps.clients.exceptions.client import ClientRoleNotMatchingWithRequiredException
from core.apps.clients.services.client_auth import BaseClientAuthService
from core.apps.common.authentication.token import BaseTokenService
from core.apps.common.models import (
    ClientRole,
    TokenType,
)


@pytest.fixture
def create_client_with_password(client_create, generate_password, hash_password):
    plain_password = generate_password()
    hashed_password = hash_password(plain_password)
    client = client_create(password=hashed_password)
    return client, plain_password


@pytest.mark.django_db
def test_client_password_validation_success(
        client_auth_service: BaseClientAuthService,
        create_client_with_password,
):
    client, plain_password = create_client_with_password

    assert client_auth_service.validate_password(
        email=client.email,
        plain_password=plain_password,
    ) is None


@pytest.mark.django_db
def test_client_password_validation_failure(
        client_auth_service: BaseClientAuthService,
        create_client_with_password,
        generate_password,
):
    client, plain_password = create_client_with_password
    new_plain_password = generate_password()
    with pytest.raises(InvalidAuthDataException):
        client_auth_service.validate_password(
            email=client.email,
            plain_password=new_plain_password,
        )


@pytest.mark.django_db
def test_client_role_check_success(client_auth_service: BaseClientAuthService, client_create):
    client_headman = client_create(roles=[RoleModelFactory(id=ClientRole.HEADMAN)])
    client_admin = client_create(roles=[RoleModelFactory(id=ClientRole.ADMIN)])

    admin_roles = [ClientRole(role.id) for role in client_admin.roles.all()]
    headman_roles = [ClientRole(role.id) for role in client_headman.roles.all()]

    assert client_auth_service.check_client_role(
        client_roles=headman_roles,
        required_role=ClientRole.HEADMAN,
    ) is None
    assert client_auth_service.check_client_role(
        client_roles=admin_roles,
        required_role=ClientRole.ADMIN,
    ) is None


@pytest.mark.django_db
def test_client_role_check_failure(client_auth_service: BaseClientAuthService, client_create):
    client_headman = client_create(roles=[RoleModelFactory(id=ClientRole.HEADMAN)])
    client_admin = client_create(roles=[RoleModelFactory(id=ClientRole.ADMIN)])

    admin_roles = [ClientRole(role.id) for role in client_admin.roles.all()]
    headman_roles = [ClientRole(role.id) for role in client_headman.roles.all()]

    with pytest.raises(ClientRoleNotMatchingWithRequiredException):
        client_auth_service.check_client_role(client_roles=headman_roles, required_role=ClientRole.ADMIN)

    with pytest.raises(ClientRoleNotMatchingWithRequiredException):
        client_auth_service.check_client_role(client_roles=admin_roles, required_role=ClientRole.HEADMAN)


@pytest.mark.django_db
def test_generate_client_tokens(
        client_auth_service: BaseClientAuthService,
        token_service: BaseTokenService,
        client_create,
        get_current_timestamp,
):
    client = client_create()
    client_entity = ClientEntity(
        id=client.id,
        first_name=client.first_name,
        last_name=client.last_name,
        email=client.email,
        middle_name=client.middle_name,
        roles=[ClientRole(role.id) for role in client.roles.all()],
    )
    tokens = client_auth_service.generate_tokens(client=client_entity)

    assert tokens.access_token is not None
    assert tokens.refresh_token is not None
    assert (
        token_service.get_device_id_from_token(token=tokens.access_token) ==
        token_service.get_device_id_from_token(token=tokens.refresh_token)
    )
    assert token_service.get_token_type_from_token(token=tokens.access_token) == TokenType.ACCESS
    assert token_service.get_token_type_from_token(token=tokens.refresh_token) == TokenType.REFRESH
    assert token_service.get_expiration_time_from_token(token=tokens.access_token) > get_current_timestamp
    assert token_service.get_expiration_time_from_token(token=tokens.refresh_token) > get_current_timestamp
    assert token_service.get_client_role_from_token(token=tokens.access_token) == client_entity.roles
    assert token_service.get_client_role_from_token(token=tokens.refresh_token) == client_entity.roles
    assert token_service.get_client_email_from_token(token=tokens.access_token) == client_entity.email
    assert token_service.get_client_email_from_token(token=tokens.refresh_token) == client_entity.email


@pytest.mark.django_db
def test_update_access_token(
        client_auth_service: BaseClientAuthService,
        token_service: BaseTokenService,
        client_create,
        get_current_timestamp,
        generate_device_id,
):
    client = client_create()
    client_entity = ClientEntity(
        id=client.id,
        first_name=client.first_name,
        last_name=client.last_name,
        email=client.email,
        middle_name=client.middle_name,
        roles=[ClientRole(role.id) for role in client.roles.all()],
    )
    tokens = client_auth_service.update_access_token(client=client_entity, device_id=generate_device_id)

    assert tokens.access_token is not None
    assert tokens.refresh_token is None
    assert token_service.get_token_type_from_token(token=tokens.access_token) == TokenType.ACCESS
    assert token_service.get_client_email_from_token(token=tokens.access_token) == client_entity.email
    assert token_service.get_client_role_from_token(token=tokens.access_token) == client_entity.roles
    assert token_service.get_expiration_time_from_token(token=tokens.access_token) > get_current_timestamp
